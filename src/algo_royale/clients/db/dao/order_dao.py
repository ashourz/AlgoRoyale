from algo_royale.clients.db.dao.base_dao import BaseDAO


class OrderDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_orders_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch orders by their status.
        :param status: The status of the orders to fetch (e.g., 'open', 'closed').
        :param limit: The maximum number of orders to fetch.
        :param offset: The offset for pagination.
        :return: List of orders with the specified status.
        """
        return self.fetch("get_orders_by_status.sql", (status, limit, offset))

    def fetch_orders_by_symbol_and_status(
        self, symbol: str, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch orders by symbol and status.
        :param symbol: The stock symbol of the orders to fetch.
        :param status: The status of the orders to fetch (e.g., 'open', 'closed').
        :param limit: The maximum number of orders to fetch.
        :param offset: The offset for pagination.
        :return: List of orders matching the specified symbol and status.
        """
        return self.fetch(
            "get_orders_by_symbol_and_status.sql", (symbol, status, limit, offset)
        )

    def insert_order(
        self,
        symbol: str,
        market: str,
        order_type: str,
        status: str,
        action: str,
        quantity: int,
        price: float,
        signal_id: str,
        user_id: str,
        account_id: str,
    ) -> int:
        """
        Insert a new order into the database.
        :param symbol: The stock symbol of the order.
        :param order_type: The type of the order (e.g., 'market', 'limit').
        :param market: The market where the order is placed (e.g., 'NYSE', 'NASDAQ').
        :param status: The status of the order (e.g., 'open', 'closed').
        :param action: The action of the order (e.g., 'buy', 'sell').
        :param quantity: The quantity of the order.
        :param price: The price at which the order was placed.
        :param signal_id: The ID of the signal associated with the order.
        :param user_id: The ID of the user who placed the order.
        :param account_id: The ID of the account associated with the order.
        :return: The ID of the newly inserted order.
        """
        return self.insert(
            "insert_order.sql",
            (
                symbol,
                market,
                order_type,
                status,
                action,
                quantity,
                price,
                signal_id,
                user_id,
                account_id,
            ),
        )

    def update_order_status(
        self,
        order_id: int,
        status: str,
    ) -> int:
        """
        Update an existing order in the database.
        :param order_id: The ID of the order to update.
        :param status: The new status of the order.
        :return: The ID of the updated order.
        """
        return self.insert(
            "update_order.sql",
            (
                status,
                order_id,
            ),
        )

    def delete_order(self, order_id: int) -> int:
        """
        Delete an order by its ID.
        :param order_id: The ID of the order to delete.
        :return: The ID of the deleted order.
        """
        return self.insert("delete_order.sql", (order_id,))

    def delete_all_orders(self) -> int:
        """
        Delete all orders from the database.
        :return: The count of deleted orders.
        """
        deleted_ids = self.insert("delete_all_orders.sql", ())
        return len(deleted_ids) if deleted_ids else 0
        # Note: This method returns the count of deleted orders, which can be useful for logging
