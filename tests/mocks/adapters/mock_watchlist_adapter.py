from algo_royale.adapters.trading.watchlist_adapter import WatchlistAdapter
from tests.mocks.clients.alpaca.mock_alpaca_watchlist_client import (
    MockAlpacaWatchlistClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockWatchlistAdapter(WatchlistAdapter):
    def __init__(self):
        client = MockAlpacaWatchlistClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False
