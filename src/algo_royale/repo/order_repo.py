from abc import ABC
from logging import Logger
from uuid import UUID

from algo_royale.clients.db.dao.order_dao import OrderDAO
from algo_royale.models.db.db_order import DBOrder


class DBOrderStatus(ABC):
    NEW = "new"
    FILL = "fill"
    PARTIAL_FILL = "partial_fill"
    CANCELED = "canceled"
    EXPIRED = "expired"
    DONE_FOR_DAY = "done_for_day"
    REPLACED = "replaced"
    REJECTED = "rejected"
    PENDING_NEW = "pending_new"
    STOPPED = "stopped"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    CALCULATED = "calculated"
    SUSPENDED = "suspended"
    ORDER_REPLACE_REJECTED = "order_replace_rejected"
    ORDER_CANCEL_REJECTED = "order_cancel_rejected"
    FAILED = "failed"


class OrderType(ABC):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderAction(ABC):
    BUY = "buy"
    SELL = "sell"


class OrderRepo:
    def __init__(self, order_dao: OrderDAO, logger: Logger):
        self.dao = order_dao
        self.logger = logger

    def fetch_order_by_id(
        self, order_id: UUID, user_id: str, account_id: str
    ) -> list[DBOrder]:
        return self.dao.fetch_order_by_id(order_id, user_id, account_id)

    def fetch_orders_by_status(
        self, status_list: list[DBOrderStatus], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        """Fetch all orders for a specific status with pagination.
        :param status_list: List of statuses to filter orders by.
        :param limit: Maximum number of orders to fetch.
        :param offset: Offset for pagination.
        :return: List of orders for the specified status.
        """
        return self.dao.fetch_orders_by_status(
            status_list=status_list, limit=limit, offset=offset
        )

    def fetch_all_orders_by_symbol_and_status(
        self, symbol: str, status_list: list[DBOrderStatus]
    ) -> list[DBOrder]:
        """Fetch orders by symbol and status with pagination.
        :param symbol: The stock symbol of the orders to fetch.
        :param status_list: List of statuses to filter orders by.
        :param limit: Maximum number of orders to fetch.
        :param offset: Offset for pagination.
        :return: List of orders matching the specified symbol and status.
        """
        return self.dao.fetch_orders_by_symbol_and_status(
            symbol=symbol, status_list=status_list
        )

    def fetch_orders_by_symbol_and_status(
        self,
        symbol: str,
        status_list: list[DBOrderStatus],
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBOrder]:
        """Fetch orders by symbol and status with pagination.
        :param symbol: The stock symbol of the orders to fetch.
        :param status_list: List of statuses to filter orders by.
        :param limit: Maximum number of orders to fetch.
        :param offset: Offset for pagination.
        :return: List of orders matching the specified symbol and status.
        """
        return self.dao.fetch_orders_by_symbol_and_status(
            symbol=symbol, status_list=status_list, limit=limit, offset=offset
        )

    def insert_order(
        self,
        symbol: str,
        order_type: OrderType,
        status: DBOrderStatus,
        action: OrderAction,
        notional: float | None,
        quantity: int | None,
        price: float | None,
    ) -> int:
        """Insert a new order record.
        :param symbol: The stock symbol of the order.
        :param order_type: The type of the order (e.g., 'market', 'limit').
        :param status: The status of the order (e.g., 'open', 'closed').
        :param action: The action of the order (e.g., 'buy', 'sell').
        :param quantity: The quantity of the order.
        :param notional: The notional value of the order.
        :param price: The price at which the order was placed.
        :param signal_id: The ID of the signal associated with the order.
        :param user_id: The ID of the user who placed the order.
        :param account_id: The ID of the account associated with the order.
        :return: The ID of the newly inserted order.
        """
        return self.dao.insert_order(
            symbol,
            order_type,
            status,
            action,
            notional,
            quantity,
            price,
            self.user_id,
            self.account_id,
        )

    def update_order_status(
        self,
        order_id: UUID,
        new_status: DBOrderStatus,
        quantity: int | None,
        price: float | None,
    ) -> int:
        """Update the status of an existing order.
        :param order_id: The ID of the order to update.
        :param new_status: The new status to set for the order (e.g., 'open', 'closed').
        :return: The number of rows affected by the update.
        """
        return self.dao.update_order_status(order_id, new_status, quantity, price)

    def delete_order(self, order_id: UUID) -> int:
        """Delete an order by its ID.
        :param order_id: The ID of the order to delete.
        :return: The number of rows affected by the deletion.
        """
        return self.dao.delete_order(order_id)

    def delete_all_orders(self) -> int:
        """Delete all orders from the database.
        :return: The number of rows affected by the deletion.
        """
        return self.dao.delete_all_orders()
