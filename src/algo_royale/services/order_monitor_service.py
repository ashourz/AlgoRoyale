from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from algo_royale.models.db.db_order import DBOrder
from algo_royale.services.clock_service import ClockService
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.trades_service import TradesService


class OrderMonitorService:
    def __init__(
        self,
        ledger_service: LedgerService,  ## Service for managing the ledger
        order_event_service: OrderEventService,  ## Incoming order events
        trades_service: TradesService,  ## Service for managing trades
        clock_service: ClockService,
        logger: Loggable,
    ):
        self.ledger_service = ledger_service
        self.order_event_service = order_event_service
        self.trade_service = trades_service
        self.order_events_subscriber = None
        self.clock_service = clock_service
        self.logger = logger

    async def async_start(self):
        """Start the order monitor service."""
        try:
            if self.order_events_subscriber is None:
                await self._async_subscribe_to_order_events()
                self.logger.info("Order stream subscriber started.")
        except Exception as e:
            self.logger.error(f"Error starting order monitor service: {e}")

    async def async_stop(self):
        """Stop the order monitor service."""
        try:
            if self.order_events_subscriber:
                await self._async_unsubscribe_from_order_events()
                self.logger.info("Order stream subscriber stopped.")
        except Exception as e:
            self.logger.error(f"Error stopping order monitor service: {e}")

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

    def _handle_order_event(self, data: OrderStreamData):
        """Handle incoming order events from the order stream."""
        try:
            self.logger.info(f"Handling order event: {data}")
            self._update_order_status(data=data)
            if data.event in [OrderStreamEvent.FILL, OrderStreamEvent.PARTIAL_FILL]:
                self._handle_fill_event(data.order)
        except Exception as e:
            self.logger.error(f"Error handling order event: {e}")

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

            now = self.clock_service.now()

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

    def _get_existing_order(self, order_id: str) -> DBOrder:
        try:
            order = self.ledger_service.fetch_order_by_id(order_id)
            if not order:
                self.logger.warning(f"No existing order found for ID: {order_id}")
                return None
            else:
                self.logger.info(f"Found existing order: {order}")
                return order
        except Exception as e:
            self.logger.error(f"Error fetching existing order {order_id}: {e}")

    def _update_order_status(self, data: OrderStreamData):
        """
        Update the order status in the repository.
        """
        try:
            status = data.db_status
            self.ledger_service.update_order(
                order_id=data.order.id,
                status=status,
                quantity=data.position_qty,
                price=data.price,
            )
            self.logger.info(f"Order {data.order.id} status updated to {status}.")
        except Exception as e:
            self.logger.error(f"Error updating order status for {data.order.id}: {e}")
