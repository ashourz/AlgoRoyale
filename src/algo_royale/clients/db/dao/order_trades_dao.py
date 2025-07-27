from algo_royale.clients.db.dao.base_dao import BaseDAO


class OrderTradesDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_order_trades_by_order_id(
        self, order_id: int, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch trades associated with a specific order ID.
        :param order_id: The ID of the order     to fetch trades for.
        :param limit: The maximum number of trades to fetch.
        :param offset: The offset for pagination.
        :return: List of trades associated with the specified order ID.
        """
        return self.fetch("get_order_trades_by_order_id.sql", (order_id, limit, offset))

    def fetch_trade_orders_by_trade_id(
        self, trade_id: int, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch orders associated with a specific trade ID.
        :param trade_id: The ID of the trade to fetch orders for.
        :param limit: The maximum number of orders to fetch.
        :param offset: The offset for pagination.
        :return: List of orders associated with the specified trade ID.
        """
        return self.fetch("get_order_trades_by_trade_id.sql", (trade_id, limit, offset))

    def insert_order_trade(self, order_id: int, trade_id: int) -> int:
        """
        Insert a new order trade into the database.
        :param order_id: The ID of the order associated with the trade.
        :param trade_id: The ID of the trade associated with the order.
        :return: The ID of the newly inserted order trade, or -1 if the insertion failed.
        """
        inserted_id = self.insert("insert_order_trade.sql", (order_id, trade_id))
        if not inserted_id:
            self.logger.error(
                f"Failed to insert order trade for order {order_id} and trade {trade_id}."
            )
            return -1
        return inserted_id

    def delete_all_order_trades(self) -> int:
        """
        Delete all order trades from the database.
        This is a utility method for cleanup purposes.
        :return: The number of deleted order trades, or -1 if the deletion failed.
        """
        deleted_ids = self.delete("delete_all_order_trades.sql")
        return len(deleted_ids) if deleted_ids else -1
