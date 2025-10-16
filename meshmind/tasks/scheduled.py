"""Scheduled Celery tasks for expiry, consolidation, and compression."""
from __future__ import annotations

import time
from typing import Callable

from celery.schedules import crontab
from meshmind.api.memory_manager import MemoryManager
from meshmind.core.config import settings
from meshmind.core.observability import log_event, telemetry
from meshmind.db.factory import create_graph_driver
from meshmind.pipeline.compress import compress_memories
from meshmind.pipeline.consolidate import (
    ConsolidationOutcome,
    ConsolidationPlan,
    consolidate_memories,
)
from meshmind.pipeline.expire import expire_memories
from meshmind.tasks.celery_app import app

_MANAGER: MemoryManager | None = None
_sleep = time.sleep


def _compute_backoff_delay(base: float, attempt: int) -> float:
    """Return the exponential backoff delay for the given attempt."""

    base = max(base, 0.0)
    if attempt <= 0:
        return base
    return base * (2**attempt)


def _run_with_retry(operation: Callable[[], None], *, description: str) -> None:
    """Execute ``operation`` with retry/backoff semantics for maintenance writes."""

    max_attempts = max(int(getattr(settings, "MAINTENANCE_MAX_ATTEMPTS", 1)), 1)
    base_delay = float(getattr(settings, "MAINTENANCE_BASE_DELAY_SECONDS", 0.0))
    attempt = 0
    while True:
        try:
            operation()
            if attempt:
                telemetry.increment("task.maintenance.retry_success")
            return
        except Exception as exc:  # pragma: no cover - specific backend errors vary
            attempt += 1
            telemetry.increment("task.maintenance.retries")
            log_event(
                "task.maintenance.retry",
                operation=description,
                attempt=attempt,
                error=str(exc),
            )
            if attempt >= max_attempts:
                telemetry.increment("task.maintenance.failures")
                raise
            delay = _compute_backoff_delay(base_delay, attempt - 1)
            telemetry.observe("task.maintenance.backoff_seconds", delay)
            if delay > 0:
                _sleep(delay)


def _reset_manager() -> None:
    global _MANAGER
    _MANAGER = None


def _get_manager() -> MemoryManager | None:
    global _MANAGER
    if _MANAGER is not None:
        return _MANAGER

    try:
        driver = create_graph_driver()
    except Exception as exc:
        log_event("task.manager.error", error=str(exc))
        return None

    _MANAGER = MemoryManager(driver)
    return _MANAGER

# Define periodic task schedule
if hasattr(app, "conf"):
    app.conf.beat_schedule = {
        'expire-memories-every-day': {
            'task': 'meshmind.tasks.scheduled.expire_task',
            'schedule': crontab(hour=0, minute=0),
        },
        'consolidate-memories-every-6-hours': {
            'task': 'meshmind.tasks.scheduled.consolidate_task',
            'schedule': crontab(hour='*/6', minute=0),
        },
        'compress-memories-every-12-hours': {
            'task': 'meshmind.tasks.scheduled.compress_task',
            'schedule': crontab(hour='*/12', minute=0),
        },
    }


@app.task(name='meshmind.tasks.scheduled.expire_task')
def expire_task():
    """Delete expired memories based on TTL."""
    manager = _get_manager()
    if manager is None:
        return []
    log_event("task.expire.start")
    with telemetry.track_duration("task.expire.duration"):
        results = expire_memories(manager)
    telemetry.increment("task.expire.runs")
    log_event("task.expire.complete", removed=len(results))
    return results


@app.task(name='meshmind.tasks.scheduled.consolidate_task')
def consolidate_task():
    """Merge duplicate memories and summarise."""
    manager = _get_manager()
    if manager is None:
        return 0
    memories = manager.list_memories()
    log_event("task.consolidate.start", memories=len(memories))
    merged_count = 0
    removed_total = 0
    failed_batches = 0
    with telemetry.track_duration("task.consolidate.duration"):
        plan = consolidate_memories(memories)
        if isinstance(plan, ConsolidationPlan):
            skipped = dict(plan.skipped_groups)
        else:  # backward compatibility
            skipped = {}
        for outcome in plan:
            try:
                _apply_consolidation(manager, outcome)
            except Exception as exc:  # pragma: no cover - depends on backend errors
                failed_batches += 1
                log_event(
                    "task.consolidate.failure",
                    error=str(exc),
                    removed=len(outcome.removed_ids),
                )
                continue
            merged_count += 1
            removed_total += len(outcome.removed_ids)
    telemetry.increment("task.consolidate.runs")
    telemetry.gauge("task.consolidate.skipped_groups", float(len(skipped)))
    telemetry.gauge("task.consolidate.failed_batches", float(failed_batches))
    log_event(
        "task.consolidate.complete",
        merged=merged_count,
        removed=removed_total,
        skipped=skipped,
        failed=failed_batches,
    )
    return {
        "merged": merged_count,
        "removed": removed_total,
        "skipped": skipped,
        "failures": failed_batches,
    }


@app.task(name='meshmind.tasks.scheduled.compress_task')
def compress_task():
    """Compress long memories to respect token limits."""
    manager = _get_manager()
    if manager is None:
        return 0
    memories = manager.list_memories()
    log_event("task.compress.start", memories=len(memories))
    updated = 0
    with telemetry.track_duration("task.compress.duration"):
        compressed = compress_memories(memories)
        for mem in compressed:
            manager.update_memory(mem)
            updated += 1
    telemetry.increment("task.compress.runs")
    log_event("task.compress.complete", updated=updated)
    return updated


def _apply_consolidation(manager: MemoryManager, outcome: ConsolidationOutcome) -> None:
    _run_with_retry(
        lambda: manager.update_memory(outcome.updated),
        description="update_memory",
    )
    for uid in outcome.removed_ids:
        if not uid:
            continue
        _run_with_retry(
            lambda value=uid: manager.delete_memory(value),
            description="delete_memory",
        )
