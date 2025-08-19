from logging import Logger
from typing import Any, Callable

from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.queued_async_symbol_hold import (
    QueuedAsyncSymbolHold,
)
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber


class SymbolHoldManager:
    update_type = "UPDATE"

    def __init__(self, symbols: list[str], get_set_timeout: float, logger: Logger):
        self.symbols = symbols
        self._pubsub = AsyncPubSub()
        self.get_set_timeout = get_set_timeout
        self.logger = logger
        self._initialize_symbol_holds()

    def _get_symbol_hold_name(self, symbol: str) -> str:
        return f"symbol_hold_{symbol}"

    def _initialize_symbol_holds(self):
        try:
            for symbol in self.symbols:
                self._get_symbol_hold(symbol)
        except Exception as e:
            self.logger.error(f"Error initializing symbol holds: {e}")

    def _get_symbol_hold(self, symbol: str) -> QueuedAsyncSymbolHold:
        try:
            symbol_hold_name = self._get_symbol_hold_name(symbol)
            value = getattr(self, symbol_hold_name, None)
            if not isinstance(value, QueuedAsyncSymbolHold):
                self.logger.warning(
                    f"No symbol hold found for symbol: {symbol}. Creating a new one."
                )
                setattr(
                    self, symbol_hold_name, QueuedAsyncSymbolHold(logger=self.logger)
                )
                value = getattr(self, symbol_hold_name)
            return value
        except Exception as e:
            self.logger.error(f"Error getting symbol hold for {symbol}: {e}")

    async def async_set_symbol_hold(self, symbol: str, status: SymbolHoldStatus):
        try:
            await self._async_update_symbol_hold_status(symbol, status)
            await self._async_publish_symbol_holds()
        except TimeoutError:
            self.logger.warning(
                f"Setting symbol hold for {symbol} timed out after {self.get_set_timeout} seconds."
            )

    async def _async_update_symbol_hold_status(
        self, symbol: str, status: SymbolHoldStatus
    ):
        try:
            symbol_hold = self._get_symbol_hold(symbol)
            await symbol_hold.async_update(status)
        except Exception as e:
            self.logger.error(f"Error updating symbol hold for {symbol}: {e}")

    async def _async_publish_symbol_holds(self):
        try:
            symbol_status_dict = {}
            for symbol in self.symbols:
                async_symbol_hold = self._get_symbol_hold(symbol)
                symbol_status_dict[symbol] = async_symbol_hold.status
            await self._pubsub.async_publish(self.update_type, symbol_status_dict)
        except Exception as e:
            self.logger.error(f"Error publishing symbol holds: {e}")

    def subscribe(
        self,
        callback: Callable[
            [dict[str, SymbolHoldStatus], type], Any
        ],  # callback receives (data, object_type)
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

    async def shutdown(self):
        """
        Shutdown the pubsub system and cancel all tasks.
        """
        await self._pubsub.async_shutdown()
