from typing import Optional

from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_position import PositionList
from algo_royale.services.trading.positions_service import PositionsService


class PositionsRepo:
    """
    Repository for managing positions in trading.
    """

    def __init__(self, positions_service: PositionsService, logger: Loggable):
        self.positions_service = positions_service
        self.logger = logger
        self.positions: Optional[PositionList] = None

    async def get_position_list(self) -> Optional[PositionList]:
        """
        Fetches a list of currently open positions.
        """
        try:
            if self.positions:
                self.logger.info(f"Open positions fetched: {self.positions}")
                return self.positions
            open_positions = await self.positions_service.get_all_open_positions()
            if open_positions:
                self.positions = open_positions
                self.logger.info(f"Open positions updated: {self.positions}")
            else:
                self.logger.info("No open positions found.")

        except Exception as e:
            self.logger.error(f"Error fetching open positions: {e}")
        return self.positions
