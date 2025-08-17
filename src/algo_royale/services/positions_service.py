from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_position import Position


class PositionsService:
    def __init__(
        self,
        adapter: PositionsAdapter,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.adapter = adapter
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id
        self.positions: list[Position] = []

    async def get_positions(self) -> list[Position]:
        """
        Get a list of currently open positions.
        """
        try:
            return self.positions
        except Exception as e:
            self.logger.error(f"Error returning open positions: {e}")

    def get_positions_by_symbol(self, symbol: str) -> list[Position]:
        """Get positions by their symbol."""
        try:
            if not self.positions:
                self.logger.warning(f"No position data available for {symbol}.")
                return []

            filtered_positions = [pos for pos in self.positions if pos.symbol == symbol]
            return filtered_positions
        except Exception as e:
            self.logger.error(f"Error filtering positions by symbol {symbol}: {e}")
            return []

    def get_positions_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list[Position]:
        """Get positions by their status."""
        try:
            if not self.positions:
                self.logger.warning(f"No position data available for status {status}.")
                return []

            filtered_positions = [
                pos for pos in self.positions if pos.status == status
            ][offset : offset + limit]
            return filtered_positions
        except Exception as e:
            self.logger.error(f"Error filtering positions by status {status}: {e}")
            return []

    async def sync_positions(self) -> None:
        """
        Update the current positions with a new list.
        """
        try:
            positionList = await self.adapter.get_all_open_positions()
            self.positions = positionList.positions if positionList else []
            self.logger.info(f"Positions updated: {len(self.positions)} found.")
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
