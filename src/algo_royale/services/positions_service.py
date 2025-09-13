from typing import Counter

from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_position import Position
from algo_royale.repo.trade_repo import TradeRepo


class PositionsService:
    def __init__(
        self,
        positions_adapter: PositionsAdapter,
        trade_repo: TradeRepo,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.adapter = positions_adapter
        self.trade_repo = trade_repo
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
            positionList = self._fetch_open_positions_from_repo()
            self.positions = positionList
            await self.validate_positions()
            self.logger.info(f"Positions updated: {len(self.positions)} found.")
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")

    def _fetch_open_positions_from_repo(self) -> list[Position]:
        """
        Fetch open positions from the trade repository.
        """
        try:
            db_positions = self.trade_repo.fetch_open_positions()
            return [Position.from_db_position(pos) for pos in db_positions]
        except Exception as e:
            self.logger.error(f"Error fetching positions from repo: {e}")
            return []

    async def validate_positions(self) -> None:
        """
        Validate positions between Alpaca and local DB.
        Log missing, duplicate, or excess positions.
        """
        try:
            # Fetch positions from Alpaca and local DB
            alpacaPositionsList = await self.adapter.fetch_all_open_positions()
            alpaca_positions = (
                alpacaPositionsList.positions if alpacaPositionsList else []
            )
            db_positions = (
                self.positions.copy()
            )  # Use the current positions from the service

            # Build key sets for comparison (symbol, quantity, account_id)
            def pos_key(pos):
                return (pos.symbol, pos.quantity, pos.account_id)

            alpaca_keys = Counter([pos_key(pos) for pos in alpaca_positions])
            db_keys = Counter([pos_key(pos) for pos in db_positions])

            # Log missing positions (in Alpaca but not in DB)
            for key in alpaca_keys:
                if key not in db_keys:
                    self.logger.warning(f"Missing local position for Alpaca: {key}")

            # Log excess positions (in DB but not in Alpaca)
            for key in db_keys:
                if key not in alpaca_keys:
                    self.logger.warning(f"Excess local position not in Alpaca: {key}")

            # Log duplicates in Alpaca
            for key, count in alpaca_keys.items():
                if count > 1:
                    self.logger.warning(
                        f"Duplicate position in Alpaca: {key} (count={count})"
                    )

            # Log duplicates in local DB
            for key, count in db_keys.items():
                if count > 1:
                    self.logger.warning(
                        f"Duplicate position in local DB: {key} (count={count})"
                    )

        except Exception as e:
            self.logger.error(f"Error validating positions: {e}")
