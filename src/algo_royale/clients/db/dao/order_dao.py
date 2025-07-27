from algo_royale.clients.db.dao.base_dao import BaseDAO


class OrderDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_orders_by_status(self, status: str):
        """
        Fetch orders by their status.
        :param status: The status of the orders to fetch (e.g., 'open', 'closed').
        :return: List of orders with the specified status.
        """
        return self.fetch("get_orders_by_status.sql", (status,))

    def fetch_orders_by_symbol_and_status(self, symbol: str, status: str):
        """
        Fetch orders by symbol and status.
        :param symbol: The stock symbol of the orders to fetch.
        :param status: The status of the orders to fetch (e.g., 'open', 'closed').
        :return: List of orders matching the specified symbol and status.
        """
        return self.fetch("get_orders_by_symbol_and_status.sql", (symbol, status))

    def insert_order(
        self,
        symbol: str,
        order_type: str,
        status: str,
        direction: str,
        quantity: int,
        filled_quantity: int,
        price: float,
        signal_id: str,
        user_id: str,
        account_id: str,
    ):
        """
        Insert a new order into the database.
        """
        self.insert(
            "insert_order.sql",
            (
                symbol,
                order_type,
                status,
                direction,
                quantity,
                filled_quantity,
                price,
                signal_id,
                user_id,
                account_id,
            ),
        )

    def delete_order(self, order_id: int):
        """
        Delete an order by its ID.
        :param order_id: The ID of the order to delete.
        """
        self.insert("delete_order.sql", (order_id,))

    def delete_all_orders(self):
        """
        Delete all orders from the database.
        """
        self.insert("delete_all_orders.sql", ())
