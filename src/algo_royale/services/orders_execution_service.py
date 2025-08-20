from datetime import datetime

from algo_royale.application.utils.async_pubsub import AsyncPubSub
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from algo_royale.models.db.db_order import DBOrder
from algo_royale.services.order_event_service import OrderEventService
from algo_royale.services.orders_service import OrderService
from algo_royale.services.trades_service import TradesService


##TODO: add days to settle to config
class OrderExecutionServices:
    def __init__(
        self,
        order_service: OrderService,
        trade_service: TradesService,
        order_event_service: OrderEventService,
        logger: Loggable,
    ):
        self.order_service = order_service
        self.trade_service = trade_service
        self.order_event_service = order_event_service
        self.logger = logger
        self.order_stream_subscriber = None
        self._order_event_pubsub = AsyncPubSub()
        self._order_event_subscriber = None

    async def start(self) -> bool:
        """Start the order stream adapter to listen for order events."""
        try:
            await self._subscribe_to_order_stream()
            return True
        except Exception as e:
            self.logger.error(f"Error starting order stream: {e}")
        return False

    async def _subscribe_to_order_stream(self):
        """Subscribe to the order stream."""
        try:
            if self.order_stream_subscriber:
                self.logger.warning("Order stream subscriber already exists.")
                return
            async_subscriber = await self.order_event_service.async_subscribe(
                callback=self._handle_order_event
            )
            self.order_stream_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to order stream: {e}")

    async def async_unsubscribe(self):
        """Unsubscribe from the order stream."""
        try:
            if not self.order_stream_subscriber:
                self.logger.warning("Order stream subscriber does not exist.")
                return
            await self.order_event_service.async_unsubscribe(
                self.order_stream_subscriber
            )
            self.order_stream_subscriber = None
        except Exception as e:
            self.logger.error(f"Error unsubscribing from order stream: {e}")

    async def stop(self) -> bool:
        """Stop the order stream adapter."""
        try:
            await self.async_unsubscribe()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping order stream: {e}")
            return False

    def _handle_order_event(self, data: OrderStreamData):
        """Handle incoming order events from the order stream."""
        try:
            self.logger.info(f"Handling order event: {data}")
            self._update_order_status(data.order.order_id, data.event)
            if data.event in [OrderStreamEvent.FILL, OrderStreamEvent.PARTIAL_FILL]:
                self._handle_fill_event(data.order)
        except Exception as e:
            self.logger.error(f"Error handling order event: {e}")

    def _update_order_status(self, order_id: str, event: OrderStreamEvent):
        """
        Update the order status in the repository.
        """
        try:
            status = event.db_status
            self.order_service.update_order_status(order_id, status)
            self.logger.info(f"Order {order_id} status updated to {status}.")
        except Exception as e:
            self.logger.error(f"Error updating order status for {order_id}: {e}")

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
