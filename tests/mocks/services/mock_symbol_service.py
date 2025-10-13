from algo_royale.services.symbol_service import SymbolService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo
from tests.mocks.services.mock_positions_service import MockPositionsService


class MockSymbolService(SymbolService):
    def __init__(self):
        super().__init__(
            watchlist_repo=MockWatchlistRepo(),
            positions_service=MockPositionsService(),
            logger=MockLoggable(),
        )
        self.base_symbols = ["AAPL", "MSFT", "GOOGL"]
        self.symbols = self.base_symbols.copy()
        self.raise_exception = False
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.symbols = self.base_symbols.copy()
        self.raise_exception = False
        self.return_empty = False

    def get_symbols(self):
        if self.raise_exception:
            raise Exception("Mocked exception")
        if self.return_empty:
            return []
        return self.symbols
