import asyncio
from typing import Any, Callable, Dict

from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.utils.queued_async_update_object import (
    QueuedAsyncUpdateObject,
)
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.events.async_pubsub import AsyncPubSub, AsyncSubscriber


##TODO: THIS PROB WONT BE NEEDED I DONT THINK ITS THE CORRECT STRUCTURE
class StreamSignalRosterObject(QueuedAsyncUpdateObject):
    """
    This class manages the roster of signals for a specific symbol.
    """

    update_type = "UPDATE"

    def __init__(self, logger=None):
        self.get_set_lock = asyncio.Lock()
        self.data: Dict[str, SignalDataPayload] = {}
        self._pubsub = AsyncPubSub()
        super().__init__(logger=logger)

    async def add_signal(self, symbol: str, signal: SignalType):
        """Add or update signal for a symbol asynchronously."""
        async with self.get_set_lock:
            current = self.data.get(symbol, (SignalType.NONE, 0.0))
            self.data[symbol] = (signal, current[1])
        await self._pubsub.publish(
            self.update_type, symbol=symbol, signal=signal, price=current[1]
        )

    async def add_signals_data_payload(self, symbol: str, payload: SignalDataPayload):
        """Add or update price for a symbol asynchronously."""
        async with self.get_set_lock:
            self.data[symbol] = payload
        await self._pubsub.publish(
            self.update_type,
            symbol=symbol,
            signal=payload.signals,
            price=payload.price_data,
        )

    def subscribe(
        self,
        callback: Callable[[dict, type], Any],  # callback receives (data, object_type)
        queue_size: int = 1,
    ) -> AsyncSubscriber:
        """Subscribe to updates with a callback."""
        return self._pubsub.subscribe(
            event_type=self.update_type, callback=callback, queue_size=queue_size
        )

    def unsubscribe(self, subscriber: AsyncSubscriber):
        """
        Unsubscribe a subscriber from the pubsub system.
        """
        self._pubsub.unsubscribe(subscriber)
