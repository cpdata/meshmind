"""Celery application setup for MeshMind maintenance tasks."""

from __future__ import annotations

from celery import Celery

from meshmind.core.config import settings


def _create_celery_app() -> Celery:
    """Initialise the Celery application bound to the configured Redis broker."""

    app = Celery(
        "meshmind",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )
    app.conf.result_backend = settings.REDIS_URL
    app.conf.task_serializer = "json"
    app.conf.result_serializer = "json"
    app.conf.accept_content = ["json"]
    app.conf.timezone = "UTC"
    app.conf.enable_utc = True
    app.conf.broker_connection_retry_on_startup = True
    return app


app = _create_celery_app()


__all__ = ["app", "_create_celery_app"]
