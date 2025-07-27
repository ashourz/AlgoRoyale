from algo_royale.clients.db.dao.base_dao import BaseDAO


class PositionTradesDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_position_trades_by_position_id(
        self, position_id: int, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch trades associated with a specific position ID.
        :param position_id: The ID of the position to fetch trades for.
        :param limit: The maximum number of trades to fetch.
        :param offset: The offset for pagination.
        :return: List of trades associated with the specified position ID.
        """
        return self.fetch(
            "get_position_trades_by_position_id.sql", (position_id, limit, offset)
        )

    def fetch_position_trades_by_trade_id(
        self, trade_id: int, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch trades associated with a specific trade ID.
        :param trade_id: The ID of the trade to fetch trades for.
        :param limit: The maximum number of trades to fetch.
        :param offset: The offset for pagination.
        :return: List of trades associated with the specified trade ID.
        """
        return self.fetch(
            "get_position_trades_by_trade_id.sql", (trade_id, limit, offset)
        )

    def insert_position_trade(self, position_id: int, trade_id: int) -> int:
        """
        Insert a new position trade into the database.
        :param position_id: The ID of the position associated with the trade.
        :param trade_id: The ID of the trade associated with the position.
        :return: The ID of the newly inserted position trade.
        """
        return self.insert("insert_position_trade.sql", (position_id, trade_id))

    def delete_all_position_trades(self) -> int:
        """
        Delete all position trades from the database.
        This is a utility method for cleanup purposes.
        :return: The number of deleted position trades.
        """
        deleted_ids = self.execute("delete_all_position_trades.sql")
        return len(deleted_ids) if deleted_ids else 0
