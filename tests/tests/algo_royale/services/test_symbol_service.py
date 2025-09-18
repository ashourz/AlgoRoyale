import pytest

from algo_royale.services.symbol_service import SymbolService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo
from tests.mocks.services.mock_positions_service import MockPositionsService


@pytest.fixture
def symbol_service():
    service = SymbolService(
        watchlist_repo=MockWatchlistRepo(),
        positions_service=MockPositionsService(),
        logger=MockLoggable(),
    )
    yield service


def set_return_empty(self, value: bool):
    self.watchlist_repo.set_return_empty(value)
    self.positions_service.set_return_empty(value)


def reset_return_empty(self):
    self.watchlist_repo.reset_return_empty()
    self.positions_service.reset_return_empty()


def set_raise_exception(self, value: bool):
    self.watchlist_repo.set_raise_exception(value)
    self.positions_service.set_raise_exception(value)


def reset_raise_exception(self):
    self.watchlist_repo.reset_raise_exception()
    self.positions_service.reset_raise_exception()


def reset(self):
    self.reset_return_empty()
    self.reset_raise_exception()


class TestSymbolService:
    def test_get_symbols_from_watchlist(self, symbol_service: SymbolService):
        symbols = symbol_service.get_symbols()
        assert symbols.sort() == ["MSFT", "GOOGL", "TSLA", "AAPL"].sort()

    def test_get_symbols_from_watchlist_empty(self, symbol_service: SymbolService):
        set_return_empty(symbol_service, True)
        symbols = symbol_service.get_symbols()
        assert symbols == []
        reset_return_empty(symbol_service)

    def test_get_symbols_from_watchlist_exception(self, symbol_service: SymbolService):
        set_raise_exception(symbol_service, True)
        symbols = symbol_service.get_symbols()
        assert symbols == []
        reset_raise_exception(symbol_service)
