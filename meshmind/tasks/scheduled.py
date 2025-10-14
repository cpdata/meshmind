"""
Scheduled Celery tasks for expiry, consolidation, and compression.
"""
from __future__ import annotations

try:
    from celery.schedules import crontab
    _CELERY_BEAT = True
except ImportError:
    # Celery not installed; define dummy crontab
    _CELERY_BEAT = False
    def crontab(*args, **kwargs):  # type: ignore
        return None
from meshmind.api.memory_manager import MemoryManager
from meshmind.core.config import settings
from meshmind.core.observability import log_event, telemetry
from meshmind.db.factory import create_graph_driver
from meshmind.pipeline.compress import compress_memories
from meshmind.pipeline.consolidate import consolidate_memories
from meshmind.pipeline.expire import expire_memories
from meshmind.tasks.celery_app import app

_MANAGER: MemoryManager | None = None


def _get_manager() -> MemoryManager | None:
    global _MANAGER
    if _MANAGER is not None:
        return _MANAGER

    try:
        driver = create_graph_driver()
    except Exception:
        return None

    _MANAGER = MemoryManager(driver)
    return _MANAGER

# Define periodic task schedule if Celery is available
if _CELERY_BEAT and hasattr(app, 'conf'):
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
    with telemetry.track_duration("task.consolidate.duration"):
        consolidated = consolidate_memories(memories)
        for mem in consolidated:
            manager.update_memory(mem)
    telemetry.increment("task.consolidate.runs")
    log_event("task.consolidate.complete", merged=len(consolidated))
    return len(consolidated)


@app.task(name='meshmind.tasks.scheduled.compress_task')
def compress_task():
    """Compress long memories to respect token limits."""
    manager = _get_manager()
    if manager is None:
        return 0
    memories = manager.list_memories()
    log_event("task.compress.start", memories=len(memories))
    with telemetry.track_duration("task.compress.duration"):
        compressed = compress_memories(memories)
        for mem in compressed:
            manager.update_memory(mem)
    telemetry.increment("task.compress.runs")
    log_event("task.compress.complete", updated=len(compressed))
    return len(compressed)
