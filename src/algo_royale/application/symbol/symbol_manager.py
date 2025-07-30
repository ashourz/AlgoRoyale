"""Keeps track of which symbols to consider for trading"""

from typing import Callable

from algo_royale.logging.loggable import Loggable


class SymbolManager:
    def __init__(
        self,
        load_watchlist: Callable[[str], list[str]],
        watchlist_path_string: str,
        logger: Loggable,
    ):
        self.logger = logger
        self.load_watchlist = load_watchlist
        self.watchlist_path_string = watchlist_path_string
        if not self.watchlist_path_string:
            raise RuntimeError("Watchlist path not specified in config")
        watchlist = self.load_watchlist(self.watchlist_path_string)
        if not watchlist:
            raise RuntimeError("Watchlist is empty")

    def _get_watchlist(self) -> list[str]:
        """
        Load the watchlist from the specified path.
        """
        return self.load_watchlist(self.watchlist_path_string)

    ## TODO: Implement a method to fetch symbols based on open positions
    def _get_open_positions(self) -> list[str]:
        """
        Get the current open positions.
        """
        return self.position_manager.get_open_positions()

    def get_symbols(self) -> list[str]:
        """
        Get the current list of symbols.
        """
        watchlist_symbols = self._get_watchlist()
        open_positions = self._get_open_positions()
        symbols = list(set(watchlist_symbols + open_positions))
        self.logger.info(f"Updated symbols: {symbols}")
        return symbols
