import asyncio
from typing import Any, Callable, Dict, List, Optional


class AsyncSubscriber:
    def __init__(
        self,
        event_type: str,
        callback: Callable[[Any], Any],
        filter_fn: Optional[Callable[[Any], bool]] = None,
        queue_size: int = 10,
    ):
        self.event_type = event_type
        self.callback = callback
        self.filter_fn = filter_fn
        self.queue = asyncio.Queue(maxsize=queue_size)
        self._task = asyncio.create_task(self._consume())

    async def _consume(self):
        try:
            while True:
                data = await self.queue.get()
                if self.filter_fn is None or self.filter_fn(data):
                    await self.callback(data)
        except asyncio.CancelledError:
            pass  # graceful exit

    async def async_send(self, data: Any):
        if self.queue.full():
            self.queue.get_nowait()  # discard oldest item if full
        await self.queue.put(data)

    def cancel(self):
        self._task.cancel()


class AsyncPubSub:
    def __init__(self):
        self.subscribers: Dict[str, List[AsyncSubscriber]] = {}

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Any], Any],
        filter_fn: Optional[Callable[[Any], bool]] = None,
        queue_size: int = 1,
    ) -> AsyncSubscriber:
        sub = AsyncSubscriber(event_type, callback, filter_fn, queue_size)
        self.subscribers.setdefault(event_type, []).append(sub)
        return sub

    async def async_publish(self, event_type: str, data: Any):
        for sub in self.subscribers.get(event_type, []):
            await sub.async_send(data)

    def unsubscribe(self, subscriber: AsyncSubscriber):
        if subscriber.event_type in self.subscribers:
            self.subscribers[subscriber.event_type].remove(subscriber)
            subscriber.cancel()

    async def async_shutdown(self):
        for subs in self.subscribers.values():
            for sub in subs:
                sub.cancel()
