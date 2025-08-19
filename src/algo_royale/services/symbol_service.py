"""Keeps track of which symbols to consider for trading"""

from algo_royale.logging.loggable import Loggable
from algo_royale.repo.watchlist_repo import WatchlistRepo
from algo_royale.services.positions_service import PositionsService


##TODO: User this when getting watchlist symbols  for trading
class SymbolService:
    def __init__(
        self,
        watchlist_repo: WatchlistRepo,
        positions_service: PositionsService,
        logger: Loggable,
    ):
        self.logger = logger
        self.watchlist_repo = watchlist_repo
        self.positions_service = positions_service

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

    async def async_get_symbols(self) -> list[str]:
        """
        Get the current list of symbols.
        """
        try:
            self.logger.info("Getting symbols...")
            # Get watchlist and open positions
            watchlist_symbols = self._get_watchlist()
            open_positions = await self.positions_service.get_positions()
            open_position_symbols = [pos.symbol for pos in open_positions]
            symbols = list(set(watchlist_symbols + open_position_symbols))
            self.logger.info(f"Got symbols: {symbols}")
            return symbols
        except Exception as e:
            self.logger.error(f"Error getting symbols: {e}")
            return []
