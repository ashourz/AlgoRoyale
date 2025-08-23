from datetime import datetime

from algo_royale.application.orders.equity_order_enums import EquityOrderSide
from algo_royale.application.orders.equity_order_types import EquityMarketNotionalOrder
from algo_royale.application.orders.signal_order_payload import SignalOrderPayload
from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.queued_async_symbol_hold import (
    QueuedAsyncSymbolHold,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from algo_royale.models.db.db_order import DBOrder
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.order_generator_service import OrderGeneratorService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.symbol_hold_service import SymbolHoldService
from algo_royale.services.trades_service import TradesService


##TODO: add days to settle to config
class OrderExecutionServices:
    def __init__(
        self,
        ledger_service: LedgerService,  ## Service for managing the ledger
        symbol_hold_service: SymbolHoldService,  ## Service for managing symbol holds
        order_generator_service: OrderGeneratorService,  ## Service for generating order payloads
        order_event_service: OrderEventService,  ## Incoming order events
        order_service: OrderService,  ## Order service for managing orders
        trade_service: TradesService,  ## Service for managing trades
        logger: Loggable,
    ):
        self.ledger_service = ledger_service
        self.symbol_hold_service = symbol_hold_service
        self.symbol_holds = QueuedAsyncSymbolHold(logger=logger)
        self.order_generator_service = order_generator_service
        self.order_service = order_service
        self.trade_service = trade_service
        self.order_event_service = order_event_service
        self.logger = logger
        self.order_events_subscriber = None
        self.symbol_order_subscribers: dict[str, list[AsyncSubscriber]] = {}

    async def start(self, symbols) -> dict[str, AsyncSubscriber] | None:
        """Start the order stream adapter to listen for order events."""
        try:
            if self.order_events_subscriber is None:
                self.logger.info("Starting order stream subscriber.")
                await self._async_subscribe_to_order_events()
            symbol_subscriber = (
                await self.order_generator_service.subscribe_to_symbol_orders(
                    symbols=symbols, callback=self._handle_order_generation
                )
            )
            self.symbol_order_subscribers.setdefault(symbols, []).append(
                symbol_subscriber
            )
            return symbol_subscriber
        except Exception as e:
            self.logger.error(f"Error starting order stream: {e}")
        return None

    async def stop(self, symbol_subscribers: dict[str, list[AsyncSubscriber]]) -> bool:
        """Stop the order stream adapter."""
        try:
            for symbol, subscribers in symbol_subscribers.items():
                await self.order_generator_service.unsubscribe_from_symbol_orders(
                    symbols=[symbol]
                )
                self.symbol_order_subscribers.get(symbol, []).remove(subscribers)
                if not self.symbol_order_subscribers.get(symbol, []):
                    del self.symbol_order_subscribers[symbol]
            if not self.symbol_order_subscribers:
                await self._async_unsubscribe_from_order_events()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping order stream: {e}")
            return False

    async def _async_subscribe_to_symbol_hold(self):
        """Subscribe to the symbol hold stream."""
        try:
            if self.symbol_hold_service:
                self.logger.info("Starting symbol hold subscriber.")
                await self.symbol_hold_service.subscribe(
                    callback=self._handle_symbol_hold_event
                )
        except Exception as e:
            self.logger.error(f"Error subscribing to symbol hold stream: {e}")

    async def _async_subscribe_to_order_events(self):
        """Subscribe to the order stream."""
        try:
            if self.order_events_subscriber:
                self.logger.warning("Order stream subscriber already exists.")
                return
            async_subscriber = await self.order_event_service.async_subscribe(
                callback=self._handle_order_event
            )
            self.order_events_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to order stream: {e}")

    async def _async_unsubscribe_from_order_events(self):
        """Unsubscribe from the order stream."""
        try:
            if not self.order_events_subscriber:
                self.logger.warning("Order stream subscriber does not exist.")
                return
            await self.order_event_service.async_unsubscribe(
                self.order_events_subscriber
            )
            self.order_events_subscriber = None
        except Exception as e:
            self.logger.error(f"Error unsubscribing from order stream: {e}")

    def _handle_symbol_hold_event(self, data: SymbolHoldStatus):
        """Handle incoming symbol hold events from the symbol hold stream."""
        try:
            self.logger.info(f"Handling symbol hold event: {data}")
            self.symbol_holds.async_update(data)
        except Exception as e:
            self.logger.error(f"Error handling symbol hold event: {e}")

    def _handle_order_generation(self, data: SignalOrderPayload):
        """Handle incoming order generation events from the order stream."""
        try:
            self.logger.info(f"Handling order generation event: {data}")
            symbol = data.symbol
            hold_status = self.symbol_holds.status[symbol]
            match data.side:
                case EquityOrderSide.BUY:
                    self.logger.info(f"Buy order for symbol {symbol}.")
                    if hold_status is SymbolHoldStatus.BUY_ONLY:
                        self.logger.info(f"Symbol {symbol} is buy-only. Proceeding.")
                        self._submit_buy_order(data)
                    else:
                        self.logger.warning(
                            f"Cannot place buy order for symbol {symbol} as it is in SELL_ONLY hold status."
                        )
                        return
                case EquityOrderSide.SELL:
                    self.logger.info(f"Sell order for symbol {symbol}.")
                    if hold_status is SymbolHoldStatus.SELL_ONLY:
                        self.logger.info(f"Symbol {symbol} is sell-only. Proceeding.")
                        self._submit_sell_order(data)
                    else:
                        self.logger.warning(
                            f"Cannot place sell order for symbol {symbol} as it is in BUY_ONLY hold status."
                        )
                        return
                case _:
                    self.logger.warning(
                        f"Unknown order side for symbol {symbol}: {data.side}"
                    )

        except Exception as e:
            self.logger.error(f"Error handling order generation event: {e}")

    def _submit_buy_order(self, data: SignalOrderPayload):
        """Submit a buy order."""
        try:
            self.logger.info(f"Submitting buy order: {data}")
            # Implement buy order submission logic here
            ##TODO:::

            weighted_notional = self.ledger_service.calculate_weighted_notional(
                data.weight
            )
            self.order_service.submit_order(
                order=EquityMarketNotionalOrder(
                    symbol=data.symbol,
                    side=EquityOrderSide.BUY,
                    notional=weighted_notional,
                )
            )
        except Exception as e:
            self.logger.error(f"Error submitting buy order: {e}")

    def _submit_sell_order(self, data: SignalOrderPayload):
        """Submit a sell order."""
        try:
            self.logger.info(f"Submitting sell order: {data}")
            # Implement sell order submission logic here
            ##TODO::

        except Exception as e:
            self.logger.error(f"Error submitting sell order: {e}")

    def _handle_order_event(self, data: OrderStreamData):
        """Handle incoming order events from the order stream."""
        try:
            self.logger.info(f"Handling order event: {data}")
            self._update_order_status(data=data)
            if data.event in [OrderStreamEvent.FILL, OrderStreamEvent.PARTIAL_FILL]:
                self._handle_fill_event(data.order)
        except Exception as e:
            self.logger.error(f"Error handling order event: {e}")

    def _update_order_status(self, data: OrderStreamData):
        """
        Update the order status in the repository.
        """
        try:
            status = data.db_status
            self.order_service.update_order_status(
                order_id=data.order.id,
                status=status,
                quantity=data.position_qty,
                price=data.price,
            )
            self.logger.info(f"Order {data.order.id} status updated to {status}.")
        except Exception as e:
            self.logger.error(f"Error updating order status for {data.order.id}: {e}")

    def _get_existing_order(self, order_id: str) -> DBOrder:
        try:
            orders = self.order_service.fetch_order_by_id(order_id)
            if not orders:
                self.logger.warning(f"No existing order found for ID: {order_id}")
                return None
            else:
                self.logger.info(f"Found existing order: {orders[0]}")
                return orders[0]
        except Exception as e:
            self.logger.error(f"Error fetching existing order {order_id}: {e}")

    def _handle_fill_event(self, order: Order):
        """Handle fill events for an order."""
        try:
            db_order = self._get_existing_order(order.id)
            if not db_order:
                self.logger.warning(f"No existing order found for fill event: {order}")
                fill_qty = order.qty
            else:
                fill_qty = order.qty - db_order.quantity
            if fill_qty <= 0:
                self.logger.warning(
                    f"Fill quantity is zero or negative for order {order}. Ignoring."
                )
                return

            db_trades = self.trade_service.fetch_trades_by_order_id(order.id)
            db_trades_qty = sum(trade.quantity for trade in db_trades)
            db_avg_price = (
                sum(trade.price * trade.quantity for trade in db_trades) / db_trades_qty
                if db_trades_qty > 0
                else 0
            )
            filled_notional = (
                order.filled_avg_price * fill_qty if order.filled_avg_price else 0
            )
            recorded_notional = db_avg_price * db_trades_qty if db_avg_price else 0
            fill_event_notional = filled_notional - recorded_notional
            fill_price = fill_event_notional / fill_qty if fill_qty > 0 else 0

            now = datetime.now()

            self.trade_service.insert_trade(
                symbol=db_order.symbol,
                action=db_order.action,
                price=fill_price,
                quantity=fill_qty,
                executed_at=order.filled_at or now,
                order_id=db_order.id,
            )

        except Exception as e:
            self.logger.error(f"Error handling fill event for order {order}: {e}")
