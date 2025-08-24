import asyncio
from typing import Callable

from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.logging.loggable import Loggable


class SymbolHoldTracker:
    event_type = "symbol_hold"

    def __init__(self, logger: Loggable):
        self.logger = logger
        self.symbol_holds: dict[str, bool] = {}  # True if on hold, False if closed
        self.lock = asyncio.Lock()
        self._pubsub = AsyncPubSub()

    async def set_hold(self, symbol: str, on_hold: bool):
        async with self.lock:
            self.symbol_holds[symbol] = on_hold
            await self._pubsub.async_publish(
                event_type=self.event_type, data=self.symbol_holds
            )

    async def subscribe(
        self, symbol: str, callback: Callable[[dict[str, bool]], None]
    ) -> AsyncSubscriber | None:
        try:
            async_subscriber = await self._pubsub.subscribe(symbol, callback)
            if async_subscriber:
                return async_subscriber
            self.logger.warning(f"Failed to subscribe to {symbol}")
        except Exception as e:
            # Handle subscription errors
            self.logger.error(f"Error subscribing to {symbol}: {e}")

    async def unsubscribe(self, async_subscriber: AsyncSubscriber):
        try:
            self._pubsub.unsubscribe(subscriber=async_subscriber)
        except Exception as e:
            # Handle unsubscription errors
            self.logger.error(
                f"Error unsubscribing from {async_subscriber.symbol}: {e}"
            )
