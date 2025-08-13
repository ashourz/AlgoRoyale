from algo_royale.clients.db.dao.position_dao import PositionDAO
from algo_royale.logging.loggable import Loggable


class PositionRepo:
    def __init__(
        self,
        dao: PositionDAO,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.dao = dao
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    def fetch_positions_by_symbol_and_status(
        self, symbol: str, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch positions by symbol and status with pagination."""
        return self.dao.fetch_positions_by_symbol_and_status(
            symbol, status, limit, offset
        )

    def fetch_positions_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch positions by their status with pagination."""
        return self.dao.fetch_positions_by_status(status, limit, offset)

    def insert_position(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        current_price: float,
    ) -> int:
        """Insert a new position record.
        :param symbol: The stock symbol of the position.
        :param quantity: The quantity of the position.
        :param entry_price: The entry price of the position.
        :param current_price: The current price of the asset.
        :return: The ID of the newly inserted position.
        """
        return self.dao.upsert_position(
            symbol,
            quantity,
            entry_price,
            current_price,
            self.user_id,
            self.account_id,
        )

    def update_position_current_price(
        self, position_id: int, current_price: float
    ) -> None:
        """Update the current price of a position.
        :param position_id: The ID of the position to update.
        :param current_price: The new current price of the position.
        """
        self.dao.update_position_current_price(position_id, current_price)
