import asyncio
from abc import ABC, abstractmethod


class QueuedAsyncUpdateObject(ABC):
    """
    Async object that queues updates and processes only the latest per type,
    with support for type hierarchy (priority).
    """

    def __init__(self, logger=None):
        self.update_lock = asyncio.Lock()
        self.pending_updates = {}  # type -> (timestamp, object)
        self.logger = logger
        self.type_hierarchy = self._type_hierarchy()

    @abstractmethod
    def _type_hierarchy(self):
        """
        Set the type hierarchy mapping: type -> priority (int).
        """
        return {}

    async def async_update(self, obj):
        """
        Queue an update object by its type.
        If a higher-priority type comes in, remove lower-priority pending updates.
        """
        try:
            obj_type = type(obj)
            now = asyncio.get_event_loop().time()
            self.pending_updates[obj_type] = (now, obj)
            # Remove lower-priority types if hierarchy is set
            if self.type_hierarchy:
                obj_priority = self.type_hierarchy.get(obj_type, 0)
                to_remove = [
                    t
                    for t, _ in self.pending_updates.items()
                    if self.type_hierarchy.get(t, 0) < obj_priority
                ]
                for t in to_remove:
                    del self.pending_updates[t]
            if not self.update_lock.locked():
                async with self.update_lock:
                    # Process all pending updates in order of priority (highest first)
                    while self.pending_updates:
                        # Sort timestamp
                        sorted_updates = sorted(
                            self.pending_updates.items(),
                            key=lambda x: x[1][0],  # sort by timestamp only
                        )
                        for t, (timestamp, obj) in sorted_updates:
                            await self._update(obj)
                            del self.pending_updates[t]
        except Exception as e:
            if self.logger:
                self.logger.error(f"[{self.__class__.__name__}] Error updating: {e}")

    @abstractmethod
    async def _update(self, obj):
        """
        Implement actual update logic in subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}._update() must be implemented."
        )
