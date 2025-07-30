"""Keeps track of which symbols to consider for trading"""

from algo_royale.logging.loggable import Loggable
from algo_royale.trader.symbols.positions_repo import PositionsRepo
from algo_royale.trader.symbols.watchlist_repo import WatchlistRepo


class SymbolManager:
    def __init__(
        self,
        watchlist_repo: WatchlistRepo,
        positions_repo: PositionsRepo,
        logger: Loggable,
    ):
        self.logger = logger
        self.watchlist_repo = watchlist_repo
        self.positions_repo = positions_repo

    def _get_watchlist(self) -> list[str]:
        """
        Load the watchlist from the specified path.
        """
        try:
            self.logger.info("Loading watchlist...")
            return self.watchlist_repo.load_watchlist()
        except Exception as e:
            self.logger.error(f"Error loading watchlist: {e}")
            return []

    async def _get_open_positions(self) -> list[str]:
        """
        Get the current open positions.
        """
        try:
            self.logger.info("Fetching open positions...")
            positions_list = await self.positions_repo.get_position_list()
            positions = positions_list.positions if positions_list else []
            return [position.symbol for position in positions]
        except Exception as e:
            self.logger.error(f"Error fetching open positions: {e}")
            return []

    async def get_symbols(self) -> list[str]:
        """
        Get the current list of symbols.
        """
        try:
            self.logger.info("Getting symbols...")
            # Get watchlist and open positions
            watchlist_symbols = self._get_watchlist()
            open_positions = await self._get_open_positions()
            symbols = list(set(watchlist_symbols + open_positions))
            self.logger.info(f"Got symbols: {symbols}")
            return symbols
        except Exception as e:
            self.logger.error(f"Error getting symbols: {e}")
            return []
