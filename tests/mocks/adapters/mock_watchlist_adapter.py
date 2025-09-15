from algo_royale.adapters.trading.watchlist_adapter import WatchlistAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockWatchlistAdapter(WatchlistAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_watchlists(self, *args, **kwargs):
        if self.return_empty:
            return []
        return [{"id": "watchlist1", "symbols": ["AAPL", "GOOG"]}]
