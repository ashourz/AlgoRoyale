from algo_royale.adapters.trading.orders_adapter import OrdersAdapter
from algo_royale.application.orders.equity_order_types import EquityMarketNotionalOrder
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.enums import OrderSide
from algo_royale.models.db.db_order import DBOrder
from algo_royale.repo.order_repo import DBOrderStatus, OrderAction, OrderRepo


class OrderService:
    def __init__(
        self,
        orders_adapter: OrdersAdapter,
        order_repo: OrderRepo,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.orders_adapter = orders_adapter
        self.order_repo = order_repo
        self.user_id = user_id
        self.account_id = account_id
        self.logger = logger

    def fetch_orders_by_symbol_and_status(
        self,
        symbol: str,
        status_list: list[DBOrderStatus],
        limit: int | None = 100,
        offset: int | None = 0,
    ):
        try:
            if limit <= 0:
                orders = self.order_repo.fetch_all_orders_by_symbol_and_status(
                    symbol=symbol, status_list=status_list
                )
            else:
                if offset < 0 | offset is None:
                    self.logger.warning("Invalid offset, defaulting to 0.")
                    offset = 0
                orders = self.order_repo.fetch_orders_by_symbol_and_status(
                    symbol=symbol, status_list=status_list, limit=limit, offset=offset
                )
            self.logger.info(f"Fetched {len(orders)} orders with status {status_list}")
            return orders
        except Exception as e:
            self.logger.error(f"Error fetching orders by status {status_list}: {e}")
            return []

    def update_order(
        self,
        order_id: str,
        status: DBOrderStatus,
        quantity: int | None,
        price: float | None,
    ) -> int:
        try:
            affected_rows = self.order_repo.update_order(
                order_id, status, quantity, price
            )
            self.logger.info(f"Updated order {order_id} status to {status}")
            return affected_rows
        except Exception as e:
            self.logger.error(
                f"Error updating order {order_id} status to {status}: {e}"
            )
            return 0

    def fetch_order_by_id(self, order_id: str) -> DBOrder | None:
        try:
            orders = self.order_repo.fetch_order_by_id(
                order_id, user_id=self.user_id, account_id=self.account_id
            )
            self.logger.info(f"Fetched order {order_id}: {orders}")
            if len(orders) > 1:
                self.logger.info(f"Multiple orders found for {order_id}: {orders}")
                return orders[0]
            elif len(orders) == 1:
                return orders[0]
            else:
                self.logger.warning(f"No orders found for {order_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching order {order_id}: {e}")
            return None

    async def submit_order(self, order: EquityMarketNotionalOrder):
        try:
            action = (
                OrderAction.BUY if order.side == OrderSide.BUY else OrderAction.SELL
            )
            client_id = self.order_repo.insert_order(
                symbol=order.symbol,
                order_type=order.order_type,
                status=DBOrderStatus.NEW,
                action=action,
                notional=order.notional,
            )
            if not client_id:
                self.logger.error(f"Failed to insert order into DB: {order}")
                return
            confirmed_order: Order = await self.orders_adapter.create_order(
                symbol=order.symbol,
                side=order.side,
                order_type=order.order_type,
                order_class=order.order_class,
                time_in_force=order.time_in_force,
                extended_hours=order.extended_hours,
                client_order_id=client_id,
                notional=order.notional,
            )
            if confirmed_order:
                self.logger.info(f"Order submitted successfully: {confirmed_order}")
            else:
                self.logger.error(f"Order submission failed for: {order}")
                self.update_order(order.client_order_id, DBOrderStatus.FAILED)
        except Exception as e:
            self.logger.error(f"Error submitting order: {order}, Error: {e}")
            self.update_order(order.client_order_id, DBOrderStatus.FAILED)
