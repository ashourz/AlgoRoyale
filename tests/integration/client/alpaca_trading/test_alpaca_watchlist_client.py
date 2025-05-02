# src: tests/integration/client/test_alpaca_account_client.py

import uuid
from algo_royale.shared.models.alpaca_trading.alpaca_watchlist import Watchlist
from algo_royale.the_risk_is_not_enough.client.alpaca_trading.alpaca_watchlist_client import AlpacaWatchlistClient
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType
import pytest


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()

@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaWatchlistClient()

@pytest.mark.asyncio
class TestAlpacaWatchlistClientIntegration:
    
    def test_watchlist_lifecycle(self, alpaca_client):
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
        logger.info("📡 Creating watchlist with name: %s and symbols: %s", original_name, symbols)
        created = alpaca_client.create_watchlist(name=original_name, symbols=symbols)
        logger.info("✅ Watchlist created: %s", created)

        assert created is not None, "❌ Failed to create watchlist"
        assert isinstance(created, Watchlist)
        assert created.name == original_name
        assert set(asset.symbol for asset in created.assets) >= set(symbols), "❌ Not all symbols were added"
        logger.info(f"✅ Watchlist '{original_name}' created with ID: {created.id}")

        watchlist_id = created.id

        # Step 2: Fetch by ID
        logger.info("🔍 Fetching watchlist by ID...")
        fetched_by_id = alpaca_client.get_watchlist_by_id(watchlist_id)
        assert fetched_by_id is not None, "❌ Could not fetch watchlist by ID"
        assert fetched_by_id.name == original_name
        logger.info("✅ Successfully fetched watchlist by ID")

        # Step 3: Fetch by Name
        logger.info("🔍 Fetching watchlist by Name...")
        fetched_by_name = alpaca_client.get_watchlist_by_name(original_name)
        assert fetched_by_name is not None, "❌ Could not fetch watchlist by name"
        assert fetched_by_name.id == watchlist_id
        logger.info("✅ Successfully fetched watchlist by Name")

        # Step 4: Fetch All
        logger.info("🔍 Fetching all watchlists...")
        all_watchlists = alpaca_client.get_all_watchlists().watchlists
        assert isinstance(all_watchlists, list), "❌ Expected list of watchlists"
        assert any(w.id == watchlist_id for w in all_watchlists), "❌ Created watchlist not found in all watchlists"
        logger.info("✅ Successfully found created watchlist in all watchlists")
        
        # Step 5: Update By ID
        updated_name = f"{original_name}_Updated"
        logger.info(f"✏️ Updating by id watchlist name to '{updated_name}'...")
        updated_watchlist = alpaca_client.update_watchlist_by_id(
            watchlist_id=watchlist_id,
            name=updated_name
        )
        assert updated_watchlist is not None, "❌ Failed to update watchlist name"
        assert updated_watchlist.name == updated_name
        logger.info("✅ Watchlist name updated successfully")

        # Step 5: Update By Name
        current_name = updated_name
        updated_name = f"{original_name}_Updated2"
        logger.info(f"✏️ Updating by name watchlist name to '{updated_name}'...")
        updated_watchlist = alpaca_client.update_watchlist_by_name(
            name=current_name,
            update_name=updated_name
        )
        assert updated_watchlist is not None, "❌ Failed to update watchlist name"
        assert updated_watchlist.name == updated_name
        logger.info("✅ Watchlist name updated successfully")
        
        # Step 6: Add a new asset
        symbol_to_add = "GOOGL"
        logger.info(f"➕ Adding asset '{symbol_to_add}' to watchlist...")
        modified_watchlist = alpaca_client.add_asset_to_watchlist_by_id(
            watchlist_id=watchlist_id,
            symbol=symbol_to_add
        )
        assert modified_watchlist is not None, "❌ Failed to add asset"
        assert any(asset.symbol == symbol_to_add for asset in modified_watchlist.assets), \
            f"❌ {symbol_to_add} was not found in the updated watchlist"        
        logger.info("✅ Asset added successfully")

        # Step 6: Remove an asset
        symbol_to_remove = "MSFT"
        logger.info("➖ Removing 'MSFT' from watchlist...")
        modified_watchlist = alpaca_client.delete_symbol_from_watchlist(
            watchlist_id=watchlist_id,
            symbol=symbol_to_remove
        )
        assert modified_watchlist is not None, "❌ Failed to remove asset"
        assert all(asset.symbol != symbol_to_remove for asset in modified_watchlist.assets), \
            f"❌ {symbol_to_remove} was found in the updated watchlist"      
        logger.info("✅ Asset removed successfully")

        # Step 7: Delete the watchlist
        logger.info("🗑️ Deleting watchlist...")
        alpaca_client.delete_watchlist_by_id(watchlist_id)
        logger.info("✅ Watchlist deleted successfully")

        # Final Check: It should not be retrievable now
        logger.info("❓ Verifying watchlist deletion...")
        try:
            should_be_none = alpaca_client.get_watchlist_by_id(watchlist_id)
        except Exception:
            should_be_none = None
        assert should_be_none is None, "❌ Watchlist still exists after deletion"
        logger.info("✅ Watchlist deletion confirmed")
        
    def test_create_watchlist_delete_by_name(self, alpaca_client):
        """
        Full lifecycle integration test:
        - Create watchlist
        - Delete watchlist
        """

        # Step 1: Create a watchlist
        original_name = f"TestWatchlist_{uuid.uuid4().hex[:8]}"
        symbols = ["AAPL", "MSFT"]
        logger.info("📡 Creating watchlist with name: %s and symbols: %s", original_name, symbols)
        created = alpaca_client.create_watchlist(name=original_name, symbols=symbols)
        logger.info("✅ Watchlist created: %s", created)

        assert created is not None, "❌ Failed to create watchlist"
        assert isinstance(created, Watchlist)
        assert created.name == original_name
        assert set(asset.symbol for asset in created.assets) >= set(symbols), "❌ Not all symbols were added"
        logger.info(f"✅ Watchlist '{original_name}' created with ID: {created.id}")

        watchlist_id = created.id

        # Step 2: Delete the watchlist
        logger.info("🗑️ Deleting watchlist...")
        alpaca_client.delete_watchlist_by_name( name = created.name )
        logger.info("✅ Watchlist deleted successfully")

        # Final Check: It should not be retrievable now
        logger.info("❓ Verifying watchlist deletion...")
        try:
            should_be_none = alpaca_client.get_watchlist_by_id(watchlist_id)
        except Exception:
            should_be_none = None
        assert should_be_none is None, "❌ Watchlist still exists after deletion"
        logger.info("✅ Watchlist deletion confirmed")