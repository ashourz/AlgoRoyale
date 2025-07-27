from algo_royale.clients.db.dao.base_dao import BaseDAO


class PositionDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_positions_by_symbol_and_status(
        self, symbol: str, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch positions for a specific symbol and status.
        :param symbol: The stock symbol of the positions to fetch.
        :param status: The status of the positions to fetch.
        :param limit: The maximum number of positions to fetch.
        :param offset: The offset for pagination.
        :return: List of positions for the specified symbol and status.
        """
        return self.fetch(
            "get_positions_by_symbol_and_status.sql", (symbol, status, limit, offset)
        )

    def fetch_positions_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """
        Fetch positions by their status.
        :param status: The status of the positions to fetch (e.g., 'open', 'closed').
        :param limit: The maximum number of positions to fetch.
        :param offset: The offset for pagination.
        :return: List of positions with the specified status.
        """
        return self.fetch("get_positions_by_status.sql", (status, limit, offset))

    def insert_position(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        current_price: float,
        unrealized_pnl: float,
        user_id: str,
        account_id: str,
    ) -> int:
        """
        Insert a new position into the database.
        :param symbol: The stock symbol of the position.
        :param quantity: The quantity of the position.
        :param entry_price: The entry price of the position.
        :param current_price: The current price of the asset.
        :param unrealized_pnl: The unrealized profit and loss for the position.
        :param user_id: The ID of the user who owns the position.
        :param account_id: The ID of the account associated with the position.
        :return: The ID of the newly inserted position.
        """
        return self.insert(
            "insert_position.sql",
            (
                symbol,
                quantity,
                entry_price,
                current_price,
                unrealized_pnl,
                user_id,
                account_id,
            ),
        )

    def update_position_current_price(
        self,
        position_id: int,
        current_price: float,
        unrealized_pnl: float,
    ) -> int:
        """
        Update an existing position.
        :param position_id: The ID of the position to update.
        :param quantity: The new quantity of the position.
        :param current_price: The current price of the asset.
        :param unrealized_pnl: The updated profit and loss for the position.
        :return: The ID of the updated position.
        """
        return self.update(
            "update_position.sql",
            (current_price, unrealized_pnl, position_id),
        )

    def delete_position(self, position_id: int) -> int:
        """
        Delete a position by its ID.
        :param position_id: The ID of the position to delete.
        :return: The ID of the deleted position.
        """
        return self.delete("delete_position.sql", (position_id,))

    def delete_all_positions(self) -> int:
        """
        Delete all positions from the database.
        :return: The count of deleted positions.
        """
        deleted_ids = self.delete("delete_all_positions.sql", ())
        return len(deleted_ids) if deleted_ids else 0
