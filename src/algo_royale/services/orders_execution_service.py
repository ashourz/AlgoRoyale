from datetime import datetime, timedelta

from algo_royale.adapters.trading.order_stream_adapter import OrderStreamAdapter
from algo_royale.application.utils.async_pubsub import AsyncPubSub
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from algo_royale.models.db.db_order import DBOrder
from algo_royale.repo.order_repo import OrderRepo
from algo_royale.repo.trade_repo import TradeRepo


##TODO: add days to settle to config
class OrderExecutionServices:
    def __init__(
        self,
        order_repo: OrderRepo,
        trade_repo: TradeRepo,
        order_stream_adapter: OrderStreamAdapter,
        logger: Loggable,
        user_id: str,
        account_id: str,
        days_to_settle: int = 1,
    ):
        self.order_repo = order_repo
        self.trade_repo = trade_repo
        self.order_stream_adapter = order_stream_adapter
        self.user_id = user_id
        self.account_id = account_id
        self.days_to_settle = days_to_settle
        self.logger = logger
        self._isStarted: bool = False
        self.order_stream_subscriber = None
        self._order_event_pubsub = AsyncPubSub()
        self._order_event_subscriber = None

    async def start_order_stream(self):
        """Start the order stream adapter to listen for order events."""
        try:
            if self._isStarted:
                self.logger.warning("Order stream already started.")
                return True

            if self.order_stream_subscriber:
                self.logger.warning("Order stream subscriber already exists.")
                return True
            self._update_settled_trades()
            self._initialize_symbol_holds()
            await self.order_stream_adapter.start()
            self.logger.info("Order stream started.")
            async_subscriber = self.order_stream_adapter.subscribe(
                callback=self._publish_order_event
            )
            if not async_subscriber:
                self.logger.error("Failed to subscribe to order stream.")
                return False
            self.order_stream_subscriber = async_subscriber
            self.logger.info("Subscribed to order stream successfully.")
            self._isStarted = True
            return True
        except Exception as e:
            self.logger.error(f"Error starting order stream: {e}")
            return False

    async def stop_order_stream(self):
        """Stop the order stream adapter."""
        try:
            if not self.order_stream_subscriber:
                self.logger.warning("Order stream not started.")
                self._isStarted = False
                return True
            await self.order_stream_adapter.stop()
            self.logger.info("Order stream stopped.")
            self.order_stream_subscriber = None
            self._isStarted = False
            return True
        except Exception as e:
            self.logger.error(f"Error stopping order stream: {e}")
            return False

    def _update_settled_trades(self):
        """Update settlement status for all trades."""
        try:
            self.logger.info("Updating settled trades...")
            settlement_datetime = datetime.now()
            updated_count = self.trade_repo.update_settled_trades(settlement_datetime)
            if updated_count == -1:
                self.logger.error("Failed to update settled trades.")
                return
            self.logger.info(f"Updated {updated_count} settled trades.")
        except Exception as e:
            self.logger.error(f"Error updating settled trades: {e}")

    def _initialize_symbol_holds(self):
        """Initialize symbol holds for the user."""
        self.logger.info("Initializing symbol holds...")
        # Fetch orders in hold status
        hold_status = [
            OrderStreamEvent.NEW,
            OrderStreamEvent.ORDER_CANCEL_REJECTED,
            OrderStreamEvent.ORDER_REPLACE_REJECTED,
            OrderStreamEvent.PARTIAL_FILL,
            OrderStreamEvent.PENDING_NEW,
            OrderStreamEvent.PENDING_CANCEL,
            OrderStreamEvent.PENDING_REPLACE,
            OrderStreamEvent.REPLACED,
            OrderStreamEvent.STOPPED,
            OrderStreamEvent.SUSPENDE,
        ]
        hold_orders: list[DBOrder] = []
        for status in hold_status:
            orders = self.order_repo.fetch_orders_by_status(status)
            hold_orders.extend(orders)

        hold_symbols = set()
        for order in hold_orders:
            hold_symbols.add(order.symbol)

        for symbol in hold_symbols:
            self._set_symbol_hold(symbol, True)

    async def _publish_order_event(self, data: OrderStreamData):
        """Publish an order event to the event bus."""
        await self._order_event_pubsub.async_publish(
            event_type="order_event", data=data
        )

    def _subscribe_to_order_events(self):
        """Subscribe to order events from the event bus."""
        self._order_event_subscriber = self._order_event_pubsub.subscribe(
            event_type="order_event", callback=self._handle_order_event, queue_size=0
        )

    def _handle_order_event(self, data: OrderStreamData):
        """Handle incoming order events from the order stream."""
        try:
            self.logger.info(f"Handling order event: {data}")
            self._update_symbol_hold(data.order.symbol, data.event)
            self._update_order_status(data.order.order_id, data.event)
            if data.event in [OrderStreamEvent.FILL, OrderStreamEvent.PARTIAL_FILL]:
                self._handle_fill_event(data.order)
        except Exception as e:
            self.logger.error(f"Error handling order event: {e}")

    def _update_symbol_hold(self, symbol: str, event: OrderStreamEvent):
        """
        Update the hold status for a symbol based on the order event.
        """
        try:
            if event in [
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
            ]:
                self._set_symbol_hold(symbol, True)
            elif event in [
                OrderStreamEvent.FILL,
                OrderStreamEvent.REJECTED,
                OrderStreamEvent.CANCELED,
                OrderStreamEvent.EXPIRED,
                OrderStreamEvent.DONE_FOR_DAY,
            ]:
                self._set_symbol_hold(symbol, False)
            self.logger.info(
                f"Updated hold status for {symbol}: {self._get_symbol_hold(symbol)}"
            )
        except Exception as e:
            self.logger.error(f"Error updating hold status for {symbol}: {e}")

    def _update_order_status(self, order_id: str, event: OrderStreamEvent):
        """
        Update the order status in the repository.
        """
        try:
            status = event.db_status
            self.order_repo.update_order_status(order_id, status)
            self.logger.info(f"Order {order_id} status updated to {status}.")
        except Exception as e:
            self.logger.error(f"Error updating order status for {order_id}: {e}")

    def _get_symbol_hold_name(self, symbol: str) -> str:
        """
        Get the hold name for a specific symbol.
        """
        return symbol + "_hold"

    def _get_symbol_hold(self, symbol: str) -> bool:
        """
        Get the hold status for a specific symbol.
        If it doesn't exist, create a new one.
        """
        hold_name = self._get_symbol_hold_name(symbol)
        value = getattr(self, hold_name, None)
        if not isinstance(value, bool):
            self.logger.warning(
                f"No hold status found for symbol: {symbol}. Creating new one."
            )
            setattr(self, hold_name, False)
            value = getattr(self, hold_name)
        return value

    def _set_symbol_hold(self, symbol: str, hold: bool):
        """Set the hold status for a specific symbol."""
        hold_name = self._get_symbol_hold_name(symbol)
        setattr(self, hold_name, hold)

    def _get_existing_order(self, order_id: str) -> DBOrder:
        try:
            orders = self.order_repo.fetch_order_by_id(
                order_id, self.user_id, self.account_id
            )
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

            db_trades = self.trade_repo.fetch_trades_by_order_id(order.id)
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
            t_plus_1 = now + timedelta(days=self.days_to_settle)

            self.trade_repo.insert_trade(
                symbol=db_order.symbol,
                market=db_order.market,
                action=db_order.action,
                settlement_data=t_plus_1,
                price=fill_price,
                quantity=fill_qty,
                executed_at=order.filled_at or now,
                order_id=db_order.id,
            )

        except Exception as e:
            self.logger.error(f"Error handling fill event for order {order}: {e}")
