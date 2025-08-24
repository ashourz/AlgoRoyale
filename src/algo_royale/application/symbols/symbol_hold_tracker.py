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
        self._roster_hold_pubsub = SymbolHoldTracker()

    async def set_hold(self, symbol: str, status: SymbolHoldStatus):
        try:
            async with self.lock:
                self.symbol_holds[symbol] = status
                symbol_event_type = self._get_symbol_event_type(symbol)
                await self._symbol_hold_pubsub.async_publish(
                    event_type=symbol_event_type, data=status
                )
                await self._roster_hold_pubsub.async_publish(
                    event_type=self.event_type, data=self.symbol_holds
                )
        except Exception as e:
            self.logger.error(f"Error setting hold for {symbol}: {e}")

    async def subscribe_to_symbol(
        self, symbol: str, callback: Callable[[SymbolHoldStatus], None]
    ) -> AsyncSubscriber | None:
        try:
            async_subscriber = await self._symbol_hold_pubsub.subscribe(
                self._get_symbol_event_type(symbol), callback
            )
            if async_subscriber:
                return async_subscriber
            self.logger.warning(f"Failed to subscribe to {symbol}")
        except Exception as e:
            # Handle subscription errors
            self.logger.error(f"Error subscribing to {symbol}: {e}")
        return None

    async def unsubscribe_from_symbol(self, async_subscriber: AsyncSubscriber):
        try:
            self._symbol_hold_pubsub.unsubscribe(subscriber=async_subscriber)
        except Exception as e:
            # Handle unsubscription errors
            self.logger.error(
                f"Error unsubscribing from {async_subscriber.symbol}: {e}"
            )

    async def subscribe_to_roster(
        self, callback: Callable[[dict[str, SymbolHoldStatus]], None]
    ) -> AsyncSubscriber | None:
        try:
            async_subscriber = await self._roster_hold_pubsub.subscribe(
                self.event_type, callback
            )
            if async_subscriber:
                return async_subscriber
            self.logger.warning("Failed to subscribe to roster holds")
        except Exception as e:
            # Handle subscription errors
            self.logger.error(f"Error subscribing to roster holds: {e}")
        return None

    async def unsubscribe_from_roster(self, async_subscriber: AsyncSubscriber):
        try:
            self._roster_hold_pubsub.unsubscribe(subscriber=async_subscriber)
        except Exception as e:
            # Handle unsubscription errors
            self.logger.error(f"Error unsubscribing from roster holds: {e}")

    def _get_symbol_event_type(self, symbol: str) -> str:
        return f"{self.event_type}_{symbol}"
