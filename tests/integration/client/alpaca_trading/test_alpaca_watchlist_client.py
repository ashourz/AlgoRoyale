# src: tests/integration/client/test_alpaca_account_client.py


import uuid
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.models.alpaca_trading.alpaca_watchlist import Watchlist
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaWatchlistClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    import copy
    from datetime import datetime

    from algo_royale.models.alpaca_trading.alpaca_asset import Asset

    # Simulate state
    watchlists_by_id = {}
    watchlists_by_name = {}

    def make_watchlist(name, symbols=None, wid=None):
        assets = []
        if symbols:
            for symbol in symbols:
                assets.append(
                    Asset(
                        id=f"asset_{symbol}",
                        class_="us_equity",
                        exchange="NASDAQ",
                        symbol=symbol,
                        name=symbol,
                        status="active",
                        tradable=True,
                        marginable=True,
                        shortable=True,
                        easy_to_borrow=True,
                        fractionable=True,
                        maintenance_margin_requirement=30,
                        attributes=[],
                    )
                )
        return Watchlist(
            id=wid or f"watchlist_{uuid.uuid4().hex[:8]}",
            account_id="account_id",
            created_at=datetime(2024, 1, 1, 9, 30, 0),
            updated_at=datetime(2024, 1, 1, 9, 31, 0),
            name=name,
            assets=assets,
        )

    async def create_watchlist_mock(name, symbols=None):
        wl = make_watchlist(name, symbols)
        watchlists_by_id[wl.id] = wl
        watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl)

    async def get_watchlist_by_name_mock(name):
        wl = watchlists_by_name.get(name)
        return copy.deepcopy(wl) if wl else None

    async def get_watchlist_by_id_mock(wid):
        wl = watchlists_by_id.get(wid)
        return copy.deepcopy(wl) if wl else None

    async def get_all_watchlists_mock():
        return type(
            "Resp",
            (),
            {"watchlists": [copy.deepcopy(wl) for wl in watchlists_by_id.values()]},
        )()

    async def update_watchlist_by_id_mock(watchlist_id, name=None, **kwargs):
        wl = watchlists_by_id.get(watchlist_id)
        if wl and name:
            del watchlists_by_name[wl.name]
            wl.name = name
            watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl) if wl else None

    async def update_watchlist_by_name_mock(name, update_name=None, **kwargs):
        wl = watchlists_by_name.get(name)
        if wl and update_name:
            del watchlists_by_name[wl.name]
            wl.name = update_name
            watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl) if wl else None

    async def add_asset_to_watchlist_by_id_mock(watchlist_id, symbol):
        wl = watchlists_by_id.get(watchlist_id)
        if wl and not any(a.symbol == symbol for a in wl.assets):
            wl.assets.append(
                Asset(
                    id=f"asset_{symbol}",
                    class_="us_equity",
                    exchange="NASDAQ",
                    symbol=symbol,
                    name=symbol,
                    status="active",
                    tradable=True,
                    marginable=True,
                    shortable=True,
                    easy_to_borrow=True,
                    fractionable=True,
                    maintenance_margin_requirement=30,
                    attributes=[],
                )
            )
        return copy.deepcopy(wl) if wl else None

    async def add_asset_to_watchlist_by_name_mock(name, symbol):
        wl = watchlists_by_name.get(name)
        if wl and not any(a.symbol == symbol for a in wl.assets):
            wl.assets.append(
                Asset(
                    id=f"asset_{symbol}",
                    class_="us_equity",
                    exchange="NASDAQ",
                    symbol=symbol,
                    name=symbol,
                    status="active",
                    tradable=True,
                    marginable=True,
                    shortable=True,
                    easy_to_borrow=True,
                    fractionable=True,
                    maintenance_margin_requirement=30,
                    attributes=[],
                )
            )
        return copy.deepcopy(wl) if wl else None

    async def delete_symbol_from_watchlist_mock(watchlist_id, symbol):
        wl = watchlists_by_id.get(watchlist_id)
        if wl:
            wl.assets = [a for a in wl.assets if a.symbol != symbol]
        return copy.deepcopy(wl) if wl else None

    async def delete_watchlist_by_id_mock(watchlist_id):
        wl = watchlists_by_id.pop(watchlist_id, None)
        if wl:
            watchlists_by_name.pop(wl.name, None)
        return True

    async def delete_watchlist_by_name_mock(name):
        wl = watchlists_by_name.pop(name, None)
        if wl:
            watchlists_by_id.pop(wl.id, None)
        return True

    # Patch methods
    monkeypatch.setattr(
        client, "create_watchlist", AsyncMock(side_effect=create_watchlist_mock)
    )
    monkeypatch.setattr(
        client,
        "get_watchlist_by_name",
        AsyncMock(side_effect=get_watchlist_by_name_mock),
    )
    monkeypatch.setattr(
        client, "get_watchlist_by_id", AsyncMock(side_effect=get_watchlist_by_id_mock)
    )
    monkeypatch.setattr(
        client, "get_all_watchlists", AsyncMock(side_effect=get_all_watchlists_mock)
    )
    monkeypatch.setattr(
        client,
        "update_watchlist_by_id",
        AsyncMock(side_effect=update_watchlist_by_id_mock),
    )
    monkeypatch.setattr(
        client,
        "update_watchlist_by_name",
        AsyncMock(side_effect=update_watchlist_by_name_mock),
    )
    monkeypatch.setattr(
        client,
        "add_asset_to_watchlist_by_id",
        AsyncMock(side_effect=add_asset_to_watchlist_by_id_mock),
    )
    monkeypatch.setattr(
        client,
        "add_asset_to_watchlist_by_name",
        AsyncMock(side_effect=add_asset_to_watchlist_by_name_mock),
    )
    monkeypatch.setattr(
        client,
        "delete_symbol_from_watchlist",
        AsyncMock(side_effect=delete_symbol_from_watchlist_mock),
    )
    monkeypatch.setattr(
        client,
        "delete_watchlist_by_id",
        AsyncMock(side_effect=delete_watchlist_by_id_mock),
    )
    monkeypatch.setattr(
        client,
        "delete_watchlist_by_name",
        AsyncMock(side_effect=delete_watchlist_by_name_mock),
    )
    yield client
    await client.aclose()


logger = MockLoggable()


@pytest.mark.asyncio
class TestAlpacaWatchlistClientIntegration:
    async def test_watchlist_lifecycle(self, alpaca_client):
        """
        Full lifecycle integration test:
        - Create watchlist
        - Fetch by name & ID
        - Fetch all
        - Update name by id & name
        - Add/Remove asset
        - Delete watchlist
        """

        # Step 1: Create a watchlist
        original_name = f"TestWatchlist_{uuid.uuid4().hex[:8]}"
        symbols = ["AAPL", "MSFT"]
        logger.info(
            "📡 Creating watchlist with name: %s and symbols: %s",
            original_name,
            symbols,
        )
        created = await alpaca_client.create_watchlist(
            name=original_name, symbols=symbols
        )
        logger.info("✅ Watchlist created: %s", created)

        assert created is not None, "❌ Failed to create watchlist"
        assert isinstance(created, Watchlist)
        assert created.name == original_name
        assert set(asset.symbol for asset in created.assets) >= set(symbols), (
            "❌ Not all symbols were added"
        )
        logger.info(f"✅ Watchlist '{original_name}' created with ID: {created.id}")

        watchlist_id = created.id

        # Step 2: Fetch by ID
        logger.info("🔍 Fetching watchlist by ID...")
        fetched_by_id = await alpaca_client.get_watchlist_by_id(watchlist_id)
        assert fetched_by_id is not None, "❌ Could not fetch watchlist by ID"
        assert fetched_by_id.name == original_name
        logger.info("✅ Successfully fetched watchlist by ID")

        # Step 3: Fetch by Name
        logger.info("🔍 Fetching watchlist by Name...")
        fetched_by_name = await alpaca_client.get_watchlist_by_name(original_name)
        assert fetched_by_name is not None, "❌ Could not fetch watchlist by name"
        assert fetched_by_name.id == watchlist_id
        logger.info("✅ Successfully fetched watchlist by Name")

        # Step 4: Fetch All
        logger.info("🔍 Fetching all watchlists...")
        response = await alpaca_client.get_all_watchlists()
        all_watchlists = response.watchlists
        assert isinstance(all_watchlists, list), "❌ Expected list of watchlists"
        assert any(w.id == watchlist_id for w in all_watchlists), (
            "❌ Created watchlist not found in all watchlists"
        )
        logger.info("✅ Successfully found created watchlist in all watchlists")

        # Step 5: Update By ID
        updated_name = f"{original_name}_Updated"
        logger.info(f"✏️ Updating by id watchlist name to '{updated_name}'...")
        updated_watchlist = await alpaca_client.update_watchlist_by_id(
            watchlist_id=watchlist_id, name=updated_name
        )
        assert updated_watchlist is not None, "❌ Failed to update watchlist name"
        assert updated_watchlist.name == updated_name
        logger.info("✅ Watchlist name updated successfully")

        # Step 5: Update By Name
        current_name = updated_name
        updated_name = f"{original_name}_Updated2"
        logger.info(f"✏️ Updating by name watchlist name to '{updated_name}'...")
        updated_watchlist = await alpaca_client.update_watchlist_by_name(
            name=current_name, update_name=updated_name
        )
        assert updated_watchlist is not None, "❌ Failed to update watchlist name"
        assert updated_watchlist.name == updated_name
        logger.info("✅ Watchlist name updated successfully")

        # Step 6: Add a new asset
        symbol_to_add = "GOOGL"
        logger.info(f"➕ Adding asset '{symbol_to_add}' to watchlist...")
        modified_watchlist = await alpaca_client.add_asset_to_watchlist_by_id(
            watchlist_id=watchlist_id, symbol=symbol_to_add
        )
        assert modified_watchlist is not None, "❌ Failed to add asset"
        assert any(
            asset.symbol == symbol_to_add for asset in modified_watchlist.assets
        ), f"❌ {symbol_to_add} was not found in the updated watchlist"
        logger.info("✅ Asset added successfully")

        # Step 6: Remove an asset
        symbol_to_remove = "MSFT"
        logger.info("➖ Removing 'MSFT' from watchlist...")
        modified_watchlist = await alpaca_client.delete_symbol_from_watchlist(
            watchlist_id=watchlist_id, symbol=symbol_to_remove
        )
        assert modified_watchlist is not None, "❌ Failed to remove asset"
        assert all(
            asset.symbol != symbol_to_remove for asset in modified_watchlist.assets
        ), f"❌ {symbol_to_remove} was found in the updated watchlist"
        logger.info("✅ Asset removed successfully")

        # Step 7: Delete the watchlist
        logger.info("🗑️ Deleting watchlist...")
        await alpaca_client.delete_watchlist_by_id(watchlist_id)
        logger.info("✅ Watchlist deleted successfully")

        # Final Check: It should not be retrievable now
        logger.info("❓ Verifying watchlist deletion...")
        try:
            should_be_none = await alpaca_client.get_watchlist_by_id(watchlist_id)
        except Exception:
            should_be_none = None
        assert should_be_none is None, "❌ Watchlist still exists after deletion"
        logger.info("✅ Watchlist deletion confirmed")

    async def test_create_watchlist_delete_by_name(self, alpaca_client):
        """
        Full lifecycle integration test:
        - Create watchlist
        - Delete watchlist
        """

        # Step 1: Create a watchlist
        original_name = f"TestWatchlist_{uuid.uuid4().hex[:8]}"
        symbols = ["AAPL", "MSFT"]
        logger.info(
            "📡 Creating watchlist with name: %s and symbols: %s",
            original_name,
            symbols,
        )
        created = await alpaca_client.create_watchlist(
            name=original_name, symbols=symbols
        )
        logger.info("✅ Watchlist created: %s", created)

        assert created is not None, "❌ Failed to create watchlist"
        assert isinstance(created, Watchlist)
        assert created.name == original_name
        assert set(asset.symbol for asset in created.assets) >= set(symbols), (
            "❌ Not all symbols were added"
        )
        logger.info(f"✅ Watchlist '{original_name}' created with ID: {created.id}")

        watchlist_id = created.id

        # Step 2: Delete the watchlist
        logger.info("🗑️ Deleting watchlist...")
        await alpaca_client.delete_watchlist_by_name(name=created.name)
        logger.info("✅ Watchlist deleted successfully")

        # Final Check: It should not be retrievable now
        logger.info("❓ Verifying watchlist deletion...")
        try:
            should_be_none = await alpaca_client.get_watchlist_by_id(watchlist_id)
        except Exception:
            should_be_none = None
        assert should_be_none is None, "❌ Watchlist still exists after deletion"
        logger.info("✅ Watchlist deletion confirmed")
