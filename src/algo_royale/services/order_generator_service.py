from typing import Callable

from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.application.orders.signal_order_payload import SignalOrderPayload
from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.logging.loggable import Loggable
from algo_royale.services.symbol_hold_service import SymbolHoldService


class OrderGeneratorService:
    def __init__(
        self,
        order_generator: OrderGenerator,
        symbol_hold_service: SymbolHoldService,
        logger: Loggable,
    ):
        self.logger = logger
        self.order_generator = order_generator
        self.symbol_hold_service = symbol_hold_service
        self.symbol_hold_subscriber = None
        self.symbol_order_subscribers: dict[str, list[AsyncSubscriber]] = {}

    async def subscribe_to_symbol_orders(
        self, symbols: list[str], callback: Callable[[SignalOrderPayload], None]
    ) -> dict[str, AsyncSubscriber] | None:
        try:
            if self.symbol_hold_subscriber is None:
                self.logger.info("Initializing symbol hold subscriber.")
                self._subscribe_to_symbol_hold()
            symbol_subscribers = await self._async_subscribe_to_orders(
                symbols, callback
            )
            for symbol, subscriber in symbol_subscribers.items():
                self.symbol_order_subscribers.setdefault(symbol, []).append(subscriber)
            return symbol_subscribers
        except Exception as e:
            self.logger.error(f"Error adding symbols to hold: {e}")

    async def unsubscribe_from_symbol_orders(self, symbols: dict[str, AsyncSubscriber]):
        try:
            for symbol, subscriber in symbols.items():
                await self.order_generator.async_unsubscribe_from_order_events(
                    symbol=symbol, async_subscriber=subscriber
                )
                self.symbol_order_subscribers.get(symbol, []).remove(subscriber)
                if not self.symbol_order_subscribers.get(symbol):
                    del self.symbol_order_subscribers[symbol]
            if not self.symbol_order_subscribers:
                await self._async_unsubscribe_from_symbol_hold()
        except Exception as e:
            self.logger.error(f"Error unsubscribing from symbol orders: {e}")

    def _subscribe_to_symbol_hold(self):
        try:
            async_subscriber = self.symbol_hold_service.subscribe(
                callback=self._handle_symbol_hold
            )
            if async_subscriber is None:
                self.logger.error("Failed to subscribe to symbol hold updates.")
                return
            self.symbol_hold_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to symbol hold updates: {e}")

    async def _async_unsubscribe_from_symbol_hold(self):
        try:
            if not self.symbol_hold_subscriber:
                self.logger.warning("Symbol hold subscriber not initialized.")
                return
            self.symbol_hold_service.unsubscribe(subscriber=self.symbol_hold_subscriber)
        except Exception as e:
            self.logger.error(f"Error unsubscribing from symbol hold updates: {e}")

    def _handle_symbol_hold(self, dict: dict[str, SymbolHoldStatus]):
        for symbol, status in dict.items():
            self.logger.info(f"Symbol '{symbol}' hold status: {status}")
            match status:
                case SymbolHoldStatus.HOLD_ALL:
                    self.logger.info(f"Symbol '{symbol}' is on hold.")
                case SymbolHoldStatus.BUY_ONLY:
                    self.logger.info(f"Symbol '{symbol}' is buy only.")
                case SymbolHoldStatus.SELL_ONLY:
                    self.logger.info(f"Symbol '{symbol}' is sell only.")
                case SymbolHoldStatus.CLOSED:
                    self.logger.info(f"Symbol '{symbol}' is closed.")
                case _:
                    self.logger.warning(
                        f"Unknown hold status for symbol '{symbol}': {status}"
                    )

    async def _async_subscribe_to_orders(
        self, symbols: list[str], callback: Callable[[SignalOrderPayload], None]
    ) -> dict[str, AsyncSubscriber] | None:
        try:
            return await self.order_generator.async_subscribe_to_order_events(
                symbols=symbols, callback=callback
            )
        except Exception as e:
            self.logger.error(f"Error subscribing to order events: {e}")

    async def _async_unsubscribe_from_orders(self, symbols: dict[str, AsyncSubscriber]):
        try:
            for symbol, subscriber in symbols.items():
                await self.order_generator.async_unsubscribe_from_order_events(
                    symbol=symbol, async_subscriber=subscriber
                )
        except Exception as e:
            self.logger.error(f"Error unsubscribing from order events: {e}")
