import pytest

from tests.mocks.adapters.mock_watchlist_adapter import MockWatchlistAdapter


@pytest.fixture
def watchlist_adapter():
    adapter = MockWatchlistAdapter()
    yield adapter


class TestWatchlistAdapter:
    def test_get_watchlists(self, watchlist_adapter):
        result = pytest.run(watchlist_adapter.get_watchlists())
        assert result is not None
        assert isinstance(result, list)
        assert any("id" in w for w in result)

    def test_get_watchlists_empty(self, watchlist_adapter):
        watchlist_adapter.set_return_empty(True)
        result = pytest.run(watchlist_adapter.get_watchlists())
        assert result == []
        watchlist_adapter.reset_return_empty()
