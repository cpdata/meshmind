"""Pipeline for expiring memories with TTL."""
from datetime import datetime, timedelta, timezone
from typing import List

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory


def expire_memories(manager: MemoryManager) -> List[str]:
    """
    Delete memories whose TTL has expired.

    :param manager: MemoryManager instance for CRUD operations.
    :return: List of UUID strings of deleted memories.
    """
    expired = []
    # List all memories
    memories = manager.list_memories()
    now = datetime.now(timezone.utc)
    for mem in memories:
        ttl = getattr(mem, 'ttl_seconds', None)
        if ttl is None:
            continue
        ref = mem.created_at
        expiry_time = ref + timedelta(seconds=ttl)
        if expiry_time <= now:
            manager.delete_memory(mem.uuid)
            expired.append(str(mem.uuid))
    return expired