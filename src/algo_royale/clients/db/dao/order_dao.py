from uuid import UUID

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.models.db.db_order import DBOrder


class OrderDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_order_by_id(
        self, order_id: UUID, user_id: str, account_id: str
    ) -> list[DBOrder]:
        """
        Fetch an order by its ID, ensuring it belongs to the specified user and account.
        :param order_id: The ID of the order to fetch.
        :param user_id: The ID of the user who owns the order.
        :param account_id: The ID of the account associated with the order.
        :return: A list representing the orders, or an empty list if not found.
        """
        rows = self.fetch("fetch_order_by_id.sql", (str(order_id), user_id, account_id))
        if not rows:
            self.logger.warning(
                f"Order with ID {order_id} not found for user {user_id}."
            )
            return []
        return [DBOrder.from_tuple(row) for row in rows]

    def fetch_all_orders_by_status(self, status_list: list[str]) -> list[DBOrder]:
        """
        Fetch all orders by their status.
        :param status_list: List of statuses to filter orders by.
        :return: List of orders matching the specified statuses.
        """
        rows = self.fetch("fetch_all_orders_by_status.sql", (status_list,))
        return [DBOrder.from_tuple(row) for row in rows]

    def fetch_orders_by_status(
        self, status_list: list[str], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        """
        Fetch orders by their status.
        :param status_list: List of statuses to filter orders by.
        :param limit: The maximum number of orders to fetch.
        :param offset: The offset for pagination.
        :return: List of orders with the specified status.
        """
        rows = self.fetch("fetch_orders_by_status.sql", (status_list, limit, offset))
        return [DBOrder.from_tuple(row) for row in rows]

    def fetch_all_orders_by_symbol_and_status(
        self, status_list: list[str], status: str
    ) -> list[DBOrder]:
        """
        Fetch orders by symbol and status.
        :param symbol: The stock symbol of the orders to fetch.
        :param status_list: List of statuses to filter orders by.
        :return: List of orders matching the specified symbol and status.
        """
        rows = self.fetch(
            "fetch_all_orders_by_symbol_and_status.sql", (status_list, status)
        )
        return [DBOrder.from_tuple(row) for row in rows]

    def fetch_orders_by_symbol_and_status(
        self, symbol: str, status_list: list[str], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        """
        Fetch orders by symbol and status.
        :param symbol: The stock symbol of the orders to fetch.
        :param status_list: List of statuses to filter orders by.
        :param limit: The maximum number of orders to fetch.
        :param offset: The offset for pagination.
        :return: List of orders matching the specified symbol and status.
        """
        rows = self.fetch(
            "fetch_orders_by_symbol_and_status.sql",
            (status_list, symbol, limit, offset),
        )
        return [DBOrder.from_tuple(row) for row in rows]

    def fetch_unsettled_orders(self) -> list[DBOrder]:
        """
        Fetch all unsettled orders.
        :return: List of unsettled orders.
        """
        rows = self.fetch("fetch_unsettled_orders.sql")
        return [DBOrder.from_tuple(row) for row in rows]

    def insert_order(
        self,
        symbol: str,
        order_type: str,
        status: str,
        action: str,
        notional: float | None,
        quantity: int | None,
        price: float | None,
        user_id: str,
        account_id: str,
    ) -> UUID | None:
        """
        Insert a new order into the database.
        :param symbol: The stock symbol of the order.
        :param order_type: The type of the order (e.g., 'market', 'limit').
        :param status: The status of the order (e.g., 'open', 'closed').
        :param action: The action of the order (e.g., 'buy', 'sell').
        :param quantity: The quantity of the order.
        :param notional: The notional value of the order.
        :param price: The price at which the order was placed.
        :param user_id: The ID of the user who placed the order.
        :param account_id: The ID of the account associated with the order.
        :return: The ID of the newly inserted order, or -1 if the insertion failed.
        """
        inserted_id = self.insert(
            "insert_order.sql",
            (
                symbol,
                order_type,
                status,
                action,
                notional,
                quantity,
                price,
                user_id,
                account_id,
            ),
        )
        if not inserted_id:
            self.logger.error(
                f"Failed to insert order for symbol {symbol} with action {action}."
            )
            return None
        return inserted_id

    def update_order(
        self,
        order_id: UUID,
        status: str,
        quantity: int,
        price: float,
    ) -> int:
        """
        Update an existing order in the database.
        :param order_id: The ID of the order to update.
        :param status: The new status of the order.
        :param quantity: The new quantity of the order.
        :param price: The new price of the order.
        :return: The ID of the updated order, or -1 if the update failed.
        """
        update_count = self.update(
            "update_order.sql",
            (
                status,
                quantity,
                price,
                str(order_id),
            ),
        )
        if not update_count:
            self.logger.error(f"Failed to update order {order_id} to status {status}.")
            return -1
        return update_count

    def update_order_as_settled(self, order_id: UUID) -> int:
        """
        Update an order's status to settled.
        :param order_id: The ID of the order to update.
        :return: The ID of the updated order, or -1 if the update failed.
        """
        update_count = self.update(
            "update_order_as_settled.sql",
            (str(order_id),),
        )
        if not update_count:
            self.logger.error(f"Failed to update order {order_id} to settled.")
            return -1
        return update_count

    def delete_order(self, order_id: UUID) -> int:
        """
        Delete an order by its ID.
        :param order_id: The ID of the order to delete.
        :return: The ID of the deleted order, or -1 if the deletion failed.
        """
        deleted_id = self.delete("delete_order.sql", (str(order_id),))
        if not deleted_id:
            self.logger.error(f"Failed to delete order {order_id}.")
            return -1
        return deleted_id

    def delete_all_orders(self) -> int:
        """
        Delete all orders from the database.
        :return: The count of deleted orders, or -1 if the deletion failed.
        """
        deleted_ids = self.delete("delete_all_orders.sql", ())
        return len(deleted_ids) if deleted_ids else -1
