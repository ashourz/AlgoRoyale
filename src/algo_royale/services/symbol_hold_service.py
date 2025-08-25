import asyncio
from logging import Logger
from typing import Any, Callable

from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.symbol_hold_tracker import SymbolHoldTracker
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.models.alpaca_trading.enums.enums import OrderSide
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from algo_royale.repo.order_repo import DBOrderStatus
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.symbol_service import SymbolService
from algo_royale.services.trades_service import TradesService


class SymbolHoldService:
    HOLD_ALL_EVENTS = [
        OrderStreamEvent.NEW,
        OrderStreamEvent.ORDER_CANCEL_REJECTED,
        OrderStreamEvent.ORDER_REPLACE_REJECTED,
        OrderStreamEvent.PARTIAL_FILL,
        OrderStreamEvent.PENDING_NEW,
        OrderStreamEvent.PENDING_CANCEL,
        OrderStreamEvent.PENDING_REPLACE,
        OrderStreamEvent.REPLACED,
        OrderStreamEvent.STOPPED,
        OrderStreamEvent.SUSPENDED,
    ]

    SELL_ONLY_OR_BUY_ONLY_EVENTS = {
        OrderStreamEvent.REJECTED,
        OrderStreamEvent.CANCELED,
        OrderStreamEvent.EXPIRED,
    }

    def __init__(
        self,
        symbol_service: SymbolService,
        symbol_hold_tracker: SymbolHoldTracker,
        order_service: OrderService,
        order_event_service: OrderEventService,
        position_service: PositionsService,
        trades_service: TradesService,
        logger: Logger,
        post_fill_delay_seconds: float,  ## TODO: move to config as 60
    ):
        self.symbol_service = symbol_service
        self.symbol_hold_tracker = symbol_hold_tracker
        self.order_service = order_service
        self.order_event_service = order_event_service
        self.position_service = position_service
        self.trades_service = trades_service
        self._order_event_subscriber = None
        self.logger = logger
        self.post_fill_delay_seconds = post_fill_delay_seconds

    async def start(self):
        try:
            if self._order_event_subscriber:
                self.logger.warning("Order event subscriber already initialized.")
                return
            await self._async_initialize_symbol_holds()
            await self._async_set_symbol_holds_by_order_status()
            # Subscribe to order events to update symbol holds
            async_subscriber = await self.order_event_service.async_subscribe(
                callback=self._async_update_symbol_hold, queue_size=0
            )
            self._order_event_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error starting symbol hold service: {e}")

    async def stop(self):
        try:
            if not self._order_event_subscriber:
                self.logger.warning("Order event subscriber not initialized.")
                return
            await self.order_event_service.async_unsubscribe(
                self._order_event_subscriber
            )
        except Exception as e:
            self.logger.error(f"Error stopping symbol hold service: {e}")

    async def _async_initialize_symbol_holds(self):
        """Initialize symbol holds for the user."""
        try:
            self.logger.info("Initializing symbol holds...")
            # Fetch all symbols
            symbols = await self.symbol_service.async_get_symbols()
            for symbol in symbols:
                await self._async_set_symbol_hold(symbol, SymbolHoldStatus.START)
        except Exception as e:
            self.logger.error(f"Error initializing symbol holds: {e}")

    async def _async_set_symbol_holds_by_order_status(self):
        """Set symbol holds based on order status."""
        try:
            self.logger.info("Setting symbol holds by order status...")
            # Fetch orders in hold status
            for symbol in self.symbol_service.async_get_symbols():
                # Fetch orders in hold status
                orders = self.order_service.fetch_orders_by_symbol_and_status(
                    symbol=symbol, status_list=self.HOLD_ALL_EVENTS
                )
                if len(orders) > 0:
                    for order in orders:
                        await self._async_set_symbol_hold(
                            order.symbol, SymbolHoldStatus.HOLD_ALL
                        )
                        return

                # Fetch orders in sell-only or buy-only status
                orders = self.order_service.fetch_orders_by_symbol_and_status(
                    symbol=symbol, status_list=self.SELL_ONLY_OR_BUY_ONLY_EVENTS
                )
                if len(orders) > 0:
                    for order in orders:
                        if self.position_service.get_positions_by_symbol(order.symbol):
                            await self._async_set_symbol_hold(
                                order.symbol, SymbolHoldStatus.SELL_ONLY
                            )
                        else:
                            await self._async_set_symbol_hold(
                                order.symbol, SymbolHoldStatus.BUY_ONLY
                            )
                    return

                # Fetch unsettled orders
                filled_orders = self.order_service.fetch_orders_by_symbol_and_status(
                    symbol=symbol, status_list=[DBOrderStatus.FILL]
                )

                if any(not order.settled for order in filled_orders):
                    await self._async_set_symbol_hold(
                        symbol, SymbolHoldStatus.PENDING_SETTLEMENT
                    )
                return

                # If no orders found, set symbol hold to BUY_ONLY
                await self._async_set_symbol_hold(symbol, SymbolHoldStatus.BUY_ONLY)
        except Exception as e:
            self.logger.error(f"Error setting symbol holds by order status: {e}")

    async def _async_update_symbol_hold(self, symbol: str, data: OrderStreamData):
        """
        Update the hold status for a symbol based on the order event.
        """
        try:
            if data.event in self.HOLD_ALL_EVENTS:
                await self._async_set_symbol_hold(symbol, SymbolHoldStatus.HOLD_ALL)
            elif data.event in self.SELL_ONLY_OR_BUY_ONLY_EVENTS:
                if self.position_service.get_positions_by_symbol(symbol):
                    await self._async_set_symbol_hold(
                        symbol, SymbolHoldStatus.SELL_ONLY
                    )
                else:
                    await self._async_set_symbol_hold(symbol, SymbolHoldStatus.BUY_ONLY)
            elif data.event == OrderStreamEvent.FILL:
                if data.order.side == OrderSide.BUY:
                    await self._async_set_symbol_hold(
                        symbol, SymbolHoldStatus.POST_FILL_DELAY
                    )
                    # Start background coroutine for post-fill delay
                    asyncio.create_task(self._post_fill_delay(symbol))
                elif data.order.side == OrderSide.SELL:
                    await self._async_set_symbol_hold(
                        symbol, SymbolHoldStatus.PENDING_SETTLEMENT
                    )
            elif data.event == OrderStreamEvent.DONE_FOR_DAY:
                await self._async_set_symbol_hold(
                    symbol, SymbolHoldStatus.CLOSED_FOR_DAY
                )

            self.logger.info(
                f"Updated hold status for {symbol}: {self._get_symbol_hold(symbol)}"
            )
        except Exception as e:
            self.logger.error(f"Error updating hold status for {symbol}: {e}")

    async def _post_fill_delay(self, symbol: str):
        try:
            await asyncio.sleep(self.post_fill_delay_seconds)
            await self._async_set_symbol_hold(symbol, SymbolHoldStatus.SELL_ONLY)
            self.logger.info(
                f"Post-fill delay complete for {symbol}, set to SELL_ONLY."
            )
        except Exception as e:
            self.logger.error(f"Error in post-fill delay for {symbol}: {e}")

    async def _async_set_symbol_hold(self, symbol: str, status: SymbolHoldStatus):
        try:
            await self.symbol_hold_tracker.async_set_hold(symbol, status)
        except Exception as e:
            self.logger.error(f"Error setting symbol hold for {symbol}: {e}")

    async def async_subscribe_to_symbol_holds(
        self,
        callback: Callable[[dict[str, SymbolHoldStatus], type], Any],
        queue_size: int = -1,
    ) -> AsyncSubscriber:
        try:
            return await self.symbol_hold_tracker.async_subscribe_to_symbol_holds(
                callback=callback, queue_size=queue_size
            )
        except Exception as e:
            self.logger.error(f"Error subscribing to symbol holds: {e}")
            return None

    def unsubscribe_from_symbol_holds(self, subscriber: AsyncSubscriber):
        try:
            self.symbol_hold_tracker.unsubscribe_from_symbol(subscriber)
        except Exception as e:
            self.logger.error(f"Error unsubscribing from symbol holds: {e}")

    async def async_subscribe_to_hold_roster(
        self, callback: Callable[[dict[str, SymbolHoldStatus], type], Any]
    ) -> AsyncSubscriber:
        try:
            return await self.symbol_hold_tracker.async_subscribe_to_roster(
                callback=callback
            )
        except Exception as e:
            self.logger.error(f"Error subscribing to hold roster: {e}")
            return None

    def unsubscribe_from_hold_roster(self, subscriber: AsyncSubscriber):
        try:
            self.symbol_hold_tracker.unsubscribe_from_roster(subscriber)
        except Exception as e:
            self.logger.error(f"Error unsubscribing from hold roster: {e}")
