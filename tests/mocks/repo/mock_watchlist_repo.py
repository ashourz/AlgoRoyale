from algo_royale.repo.watchlist_repo import WatchlistRepo
from tests.mocks.mock_loggable import MockLoggable


class MockWatchlistRepo(WatchlistRepo):
    def __init__(self, watchlist_path: str = "mock_watchlist.txt", logger=None):
        if logger is None:
            logger = MockLoggable()
        # Simulate file not found error for sentinel paths (to match real WatchlistRepo)
        if watchlist_path == "nonexistent.txt":
            raise FileNotFoundError(f"Watchlist file not found at: {watchlist_path}")
        self.watchlist_path = watchlist_path
        self.logger = logger
        self.test_watchlist = ["AAPL", "GOOGL", "MSFT"]
        self.return_empty = False
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset_watchlist(self):
        self.test_watchlist = ["AAPL", "GOOGL", "MSFT"]

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
        self.reset_watchlist()

    def load_watchlist(self) -> list[str]:
        if self.raise_exception:
            raise FileNotFoundError("Simulated exception in load_watchlist")
        if self.return_empty:
            return []
        return self.test_watchlist

    def save_watchlist(self, symbols: list[str]):
        if self.raise_exception:
            raise ValueError("Simulated exception in save_watchlist")
        self.test_watchlist = symbols
