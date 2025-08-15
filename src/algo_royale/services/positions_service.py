from typing import Optional

from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_position import PositionList
from algo_royale.repo.position_repo import PositionRepo


class PositionsService:
    def __init__(
        self,
        repo: PositionRepo,
        adapter: PositionsAdapter,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.repo = repo
        self.adapter = adapter
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    async def get_position_list(self) -> Optional[PositionList]:
        """
        Fetches a list of currently open positions.
        """
        try:
            if self.positions:
                self.logger.info(f"Open positions fetched: {self.positions}")
                return self.positions
            open_positions = await self.adapter.get_all_open_positions()
            if open_positions:
                self.positions = open_positions
                self.logger.info(f"Open positions updated: {self.positions}")
            else:
                self.logger.info("No open positions found.")

        except Exception as e:
            self.logger.error(f"Error fetching open positions: {e}")
        return self.positions

    def fetch_positions_by_symbol_and_status(
        self, symbol: str, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch positions by symbol and status with pagination."""
        return self.repo.fetch_positions_by_symbol(symbol, status, limit, offset)

    def fetch_positions_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch positions by their status with pagination."""
        return self.repo.fetch_positions_by_status(status, limit, offset)

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
        return self.repo.upsert_position(
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
        self.repo.update_position_current_price(position_id, current_price)
