import asyncio
from typing import Callable

from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.logging.loggable import Loggable


class SymbolHoldTracker:
    event_type = "symbol_hold"

    def __init__(self, logger: Loggable):
        self.logger = logger
        self.symbol_holds: dict[
            str, SymbolHoldStatus
        ] = {}  # True if on hold, False if closed
        self.lock = asyncio.Lock()
        self._symbol_hold_pubsub = AsyncPubSub()
        self._roster_hold_pubsub = AsyncPubSub()

    async def async_set_hold(self, symbol: str, status: SymbolHoldStatus):
        try:
            async with self.lock:
                self.symbol_holds[symbol] = status
                await self._symbol_hold_pubsub.async_publish(
                    event_type=self.event_type, data={symbol: status}
                )
                await self._roster_hold_pubsub.async_publish(
                    event_type=self.event_type, data=self.symbol_holds
                )
        except Exception as e:
            self.logger.error(f"Error setting hold for {symbol}: {e}")

    async def async_subscribe_to_symbol_holds(
        self,
        callback: Callable[[dict[str, SymbolHoldStatus]], None],
        queue_size: int = -1,
    ) -> AsyncSubscriber | None:
        try:
            async_subscriber = self._symbol_hold_pubsub.subscribe(
                event_type=self.event_type, callback=callback, queue_size=queue_size
            )
            if async_subscriber:
                return async_subscriber
            self.logger.warning("Failed to subscribe to symbol holds")
        except Exception as e:
            # Handle subscription errors
            self.logger.error(f"Error subscribing to symbol holds: {e}")
        return None

    def unsubscribe_from_symbol(self, async_subscriber: AsyncSubscriber):
        try:
            self._symbol_hold_pubsub.unsubscribe(subscriber=async_subscriber)
        except Exception as e:
            # Handle unsubscription errors
            self.logger.error(
                f"Error unsubscribing from {async_subscriber.symbol}: {e}"
            )

    async def async_subscribe_to_roster(
        self, callback: Callable[[dict[str, SymbolHoldStatus]], None]
    ) -> AsyncSubscriber | None:
        try:
            async_subscriber = self._roster_hold_pubsub.subscribe(
                self.event_type, callback
            )
            if async_subscriber:
                return async_subscriber
            self.logger.warning("Failed to subscribe to roster holds")
        except Exception as e:
            # Handle subscription errors
            self.logger.error(f"Error subscribing to roster holds: {e}")
        return None

    def unsubscribe_from_roster(self, async_subscriber: AsyncSubscriber):
        try:
            self._roster_hold_pubsub.unsubscribe(subscriber=async_subscriber)
        except Exception as e:
            # Handle unsubscription errors
            self.logger.error(f"Error unsubscribing from roster holds: {e}")
