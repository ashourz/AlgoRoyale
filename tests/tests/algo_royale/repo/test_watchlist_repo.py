import pytest

from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo


@pytest.fixture
def watchlist_repo():
    adapter = MockWatchlistRepo()
    yield adapter


@pytest.mark.asyncio
class TestWatchlistRepo:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, watchlist_repo):
        # Code to run before each test
        print("Setup")
        watchlist_repo.reset_return_empty()
        watchlist_repo.reset_raise_exception()
        watchlist_repo.reset_watchlist()
        yield
        # Code to run after each test
        print("Teardown")
        watchlist_repo.reset_return_empty()
        watchlist_repo.reset_raise_exception()
        watchlist_repo.reset_watchlist()

    async def test_load_watchlist(self, watchlist_repo):
        result = watchlist_repo.load_watchlist()
        assert result == ["AAPL", "GOOGL", "MSFT"]

    async def test_load_watchlist_empty(self, watchlist_repo):
        watchlist_repo.set_return_empty(True)
        result = watchlist_repo.load_watchlist()
        assert result == []
        watchlist_repo.reset_return_empty()

    async def test_load_watchlist_exception(self, watchlist_repo):
        watchlist_repo.set_raise_exception(True)
        with pytest.raises(FileNotFoundError):
            watchlist_repo.load_watchlist()
        watchlist_repo.reset_raise_exception()

    async def test_save_watchlist(self, watchlist_repo):
        new_symbols = ["TSLA", "AMZN"]
        watchlist_repo.save_watchlist(new_symbols)
        assert watchlist_repo.test_watchlist == new_symbols

    async def test_save_watchlist_exception(self, watchlist_repo):
        watchlist_repo.set_raise_exception(True)
        with pytest.raises(ValueError):
            watchlist_repo.save_watchlist(["TSLA", "AMZN"])
        watchlist_repo.reset_raise_exception()
