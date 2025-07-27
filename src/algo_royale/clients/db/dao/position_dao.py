from algo_royale.clients.db.dao.base_dao import BaseDAO


class PositionDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_positions_by_user(self, user_id: str):
        """
        Fetch positions for a specific user.
        :param user_id: The ID of the user whose positions to fetch.
        :return: List of positions for the specified user.
        """
        return self.fetch("get_positions_by_user.sql", (user_id,))

    def insert_position(
        self,
        symbol: str,
        quantity: int,
        average_price: float,
        user_id: str,
    ):
        """
        Insert a new position into the database.
        """
        self.insert(
            "insert_position.sql",
            (symbol, quantity, average_price, user_id),
        )

    def delete_position(self, position_id: int):
        """
        Delete a position by its ID.
        :param position_id: The ID of the position to delete.
        """
        self.delete("delete_position.sql", (position_id,))
