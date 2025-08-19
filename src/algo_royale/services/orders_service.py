from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_order import DBOrder
from algo_royale.repo.order_repo import DBOrderStatus, OrderRepo


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepo,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.order_repo = order_repo
        self.user_id = user_id
        self.account_id = account_id
        self.logger = logger

    def fetch_orders_by_status(
        self, status: DBOrderStatus, limit: int | None = 100, offset: int | None = 0
    ):
        try:
            if limit <= 0:
                orders = self.order_repo.fetch_all_orders_by_status(status)
            else:
                if offset < 0 | offset is None:
                    self.logger.warning("Invalid offset, defaulting to 0.")
                    offset = 0
                orders = self.order_repo.fetch_orders_by_status(
                    status=status, limit=limit, offset=offset
                )
            self.logger.info(f"Fetched {len(orders)} orders with status {status}")
            return orders
        except Exception as e:
            self.logger.error(f"Error fetching orders by status {status}: {e}")
            return []

    def update_order_status(self, order_id: str, status: DBOrderStatus):
        try:
            self.order_repo.update_order_status(order_id, status)
            self.logger.info(f"Updated order {order_id} status to {status}")
        except Exception as e:
            self.logger.error(
                f"Error updating order {order_id} status to {status}: {e}"
            )

    def fetch_order_by_id(self, order_id: str) -> DBOrder | None:
        try:
            order = self.order_repo.fetch_order_by_id(
                order_id, user_id=self.user_id, account_id=self.account_id
            )
            self.logger.info(f"Fetched order {order_id}: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error fetching order {order_id}: {e}")
            return None
