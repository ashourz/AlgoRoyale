import pytest

from tests.mocks.adapters.mock_watchlist_adapter import MockWatchlistAdapter


@pytest.fixture
def watchlist_adapter():
    adapter = MockWatchlistAdapter()
    yield adapter


@pytest.mark.asyncio
class TestWatchlistAdapter:
    async def test_get_all_watchlists(self, watchlist_adapter):
        # Should return a response object with a watchlists attribute (list)
        resp = await watchlist_adapter.get_all_watchlists()
        assert hasattr(resp, "watchlists")
        assert isinstance(resp.watchlists, list)

    async def test_create_and_get_watchlist_by_id(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("MyWL", ["AAPL", "GOOG"])
        assert wl is not None
        fetched = await watchlist_adapter.get_watchlist_by_id(wl.id)
        assert fetched is not None
        assert fetched.id == wl.id

    async def test_get_watchlist_by_name(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("ByName", ["MSFT"])
        fetched = await watchlist_adapter.get_watchlist_by_name("ByName")
        assert fetched is not None
        assert fetched.name == "ByName"

    async def test_update_watchlist_by_id(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("OldName", ["TSLA"])
        updated = await watchlist_adapter.update_watchlist_by_id(wl.id, "NewName")
        assert updated is not None
        assert updated.name == "NewName"

    async def test_update_watchlist_by_name(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("ToUpdate", ["NFLX"])
        updated = await watchlist_adapter.update_watchlist_by_name(
            "ToUpdate", "UpdatedName"
        )
        assert updated is not None
        assert updated.name == "UpdatedName"

    async def test_add_asset_to_watchlist_by_id(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("AssetById", ["AAPL"])
        updated = await watchlist_adapter.add_asset_to_watchlist_by_id(wl.id, "GOOG")
        assert updated is not None
        assert any(a.symbol == "GOOG" for a in updated.assets)

    async def test_add_asset_to_watchlist_by_name(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("AssetByName", ["AAPL"])
        updated = await watchlist_adapter.add_asset_to_watchlist_by_name(
            "AssetByName", "GOOG"
        )
        assert updated is not None
        assert any(a.symbol == "GOOG" for a in updated.assets)

    async def test_delete_symbol_from_watchlist(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("DelSym", ["AAPL", "GOOG"])
        updated = await watchlist_adapter.delete_symbol_from_watchlist(wl.id, "AAPL")
        assert updated is not None
        assert all(a.symbol != "AAPL" for a in updated.assets)

    async def test_delete_watchlist_by_id(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("DelById", ["AAPL"])
        result = await watchlist_adapter.delete_watchlist_by_id(wl.id)
        # Should not raise, and should return True or None
        assert result is None or result is True

    async def test_delete_watchlist_by_name(self, watchlist_adapter):
        wl = await watchlist_adapter.create_watchlist("DelByName", ["AAPL"])
        result = await watchlist_adapter.delete_watchlist_by_name("DelByName")
        assert result is None or result is True
