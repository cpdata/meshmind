"""
Celery application setup for MeshMind maintenance tasks.
If Celery is not installed, provides a dummy app for imports.
"""
try:
    from celery import Celery
except ImportError:
    Celery = None  # type: ignore

class _DummyConf:
    pass

class _DummyCeleryApp:
    def __init__(self):
        self.conf = _DummyConf()

    def task(self, name=None):
        def decorator(fn):
            return fn
        return decorator

if Celery:
    from meshmind.core.config import settings

    # Initialize Celery app with Redis broker
    app = Celery(
        'meshmind',
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )
    # Celery configuration
    app.conf.result_backend = settings.REDIS_URL
    app.conf.task_serializer = 'json'
    app.conf.result_serializer = 'json'
    app.conf.accept_content = ['json']
    app.conf.timezone = 'UTC'
    app.conf.enable_utc = True
else:
    app = _DummyCeleryApp()