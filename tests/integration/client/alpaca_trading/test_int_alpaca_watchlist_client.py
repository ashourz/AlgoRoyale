import uuid

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.utils.application_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_watchlist import Watchlist


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_watchlist_client
    try:
        yield client
    finally:
        await client_container.async_close_all_clients()


@pytest.fixture
async def test_watchlist(alpaca_client):
    # Create a unique watchlist for the test
    unique_name = f"integration_test_watchlist_{uuid.uuid4().hex[:8]}"
    watchlist = await alpaca_client.create_watchlist(unique_name, ["AAPL"])
    assert watchlist is not None and hasattr(watchlist, "id")
    yield watchlist
    # Cleanup: delete the watchlist
    try:
        await alpaca_client.delete_watchlist_by_id(watchlist.id)
    except Exception:
        pass


@pytest.mark.asyncio
class TestAlpacaWatchlistClientIntegration:
    async def test_watchlist_lifecycle(
        self, alpaca_client: AlpacaWatchlistClient, test_watchlist: Watchlist
    ):
        # Read
        fetched = await alpaca_client.fetch_watchlist_by_id(test_watchlist.id)
        assert fetched is not None and fetched.id == test_watchlist.id
        # Add asset
        updated = await alpaca_client.add_asset_to_watchlist_by_id(
            test_watchlist.id, "SNDL"
        )
        assert updated is not None and any(
            asset.symbol == "SNDL" for asset in updated.assets
        )
        # Remove asset
        updated = await alpaca_client.delete_symbol_from_watchlist(
            test_watchlist.id, "SNDL"
        )
        assert updated is not None and all(
            asset.symbol != "SNDL" for asset in updated.assets
        )
        # Update name
        new_name = test_watchlist.name + "_updated"
        updated = await alpaca_client.update_watchlist_by_id(
            test_watchlist.id, new_name
        )
        assert updated is not None and updated.name == new_name
        # Fetch by name
        fetched_by_name = await alpaca_client.fetch_watchlist_by_name(new_name)
        assert fetched_by_name is not None and fetched_by_name.id == test_watchlist.id
        # All watchlists (should include ours)
        all_lists = await alpaca_client.fetch_all_watchlists()
        assert all_lists is None or any(
            wl.id == test_watchlist.id for wl in getattr(all_lists, "watchlists", [])
        )
        # Cleanup is handled by fixture
