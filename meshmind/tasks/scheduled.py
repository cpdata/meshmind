"""
Scheduled Celery tasks for expiry, consolidation, and compression.
"""
try:
    from celery.schedules import crontab
    _CELERY_BEAT = True
except ImportError:
    # Celery not installed; define dummy crontab
    _CELERY_BEAT = False
    def crontab(*args, **kwargs):  # type: ignore
        return None
from meshmind.tasks.celery_app import app
from meshmind.pipeline.expire import expire_memories
from meshmind.pipeline.consolidate import consolidate_memories
from meshmind.pipeline.compress import compress_memories
from meshmind.api.memory_manager import MemoryManager
from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.core.config import settings

# Initialize database driver and memory manager (fallback if mgclient missing)
try:
    driver = MemgraphDriver(
        settings.MEMGRAPH_URI,
        settings.MEMGRAPH_USERNAME,
        settings.MEMGRAPH_PASSWORD,
    )
    manager = MemoryManager(driver)
except Exception:
    driver = None  # type: ignore
    manager = None  # type: ignore

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
    if manager is None:
        return []
    return expire_memories(manager)


@app.task(name='meshmind.tasks.scheduled.consolidate_task')
def consolidate_task():
    """Merge duplicate memories and summarise."""
    if manager is None:
        return 0
    memories = manager.list_memories()
    consolidated = consolidate_memories(memories)
    for mem in consolidated:
        manager.update_memory(mem)
    return len(consolidated)


@app.task(name='meshmind.tasks.scheduled.compress_task')
def compress_task():
    """Compress long memories to respect token limits."""
    if manager is None:
        return 0
    memories = manager.list_memories()
    compressed = compress_memories(memories)
    for mem in compressed:
        manager.update_memory(mem)
    return len(compressed)