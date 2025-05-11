# src: tests/integration/client/test_alpaca_account_client.py

from algo_royale.di.container import DIContainer
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from algo_royale.clients.alpaca.exceptions import AlpacaAssetNotFoundException
import pytest
from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import AlpacaAssetsClient

from algo_royale.logging.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()


@pytest.fixture
async def alpaca_client():
    client = AlpacaAssetsClient(
        trading_config=DIContainer.trading_config(),
    )
    yield client
    await client.aclose()  # Clean up the async client
    
@pytest.mark.asyncio
class TestAlpacaAssetClientIntegration:
    
    async def test_fetch_assets(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""
        try:
            result = await alpaca_client.fetch_assets()

            assert result is not None
            assert isinstance(result, list)
            assert all(isinstance(asset, Asset) for asset in result)
            assert len(result) > 0, "Expected at least one asset in the result"

            expected_attrs = [
                "id", "class_", "exchange", "symbol", "name", "status",
                "tradable", "marginable", "maintenance_margin_requirement",
                "shortable", "easy_to_borrow", "fractionable", "attributes"
            ]

            for asset in result:
                for attr in expected_attrs:
                    assert hasattr(asset, attr), f"Missing expected attribute: {attr}"
        except AlpacaAssetNotFoundException:
            return None
                
    async def test_fetch_asset_by_symbol_or_id(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""
        symbol = "AAPL"
        try:
            result = await alpaca_client.fetch_asset_by_symbol_or_id(
                symbol_or_asset_id = symbol
            )
            assert result is not None
            assert isinstance(result, Asset)

            expected_attrs = [
                "id", "class_", "exchange", "symbol", "name", "status",
                "tradable", "marginable", "maintenance_margin_requirement",
                "shortable", "easy_to_borrow", "fractionable", "attributes"
            ]

            for attr in expected_attrs:
                assert hasattr(result, attr), f"Missing expected attribute: {attr}"
        except AlpacaAssetNotFoundException:
            return None
