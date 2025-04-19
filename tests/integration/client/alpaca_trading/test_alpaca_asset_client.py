# src: tests/integration/client/test_alpaca_account_client.py

import logging
import pytest
from algo_royale.client.alapaca_trading.alpaca_assets_client import AlpacaAssetsClient
from models.alpaca_trading.alpaca_asset import Asset

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaAssetsClient()

@pytest.mark.asyncio
class TestAlpacaAssetClientIntegration:
    
    def test_fetch_assets(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""

        result = alpaca_client.fetch_assets()

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
                
    def test_fetch_asset_by_symbol_or_id(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""
        symbol = "AAPL"
        result = alpaca_client.fetch_asset_by_symbol_or_id(
            symbol_or_asset_id = symbol
        )

        if result == None:
            logger.debug(f"No asset found for {symbol}")
        else:
            assert result is not None
            assert isinstance(result, Asset)

            expected_attrs = [
                "id", "class_", "exchange", "symbol", "name", "status",
                "tradable", "marginable", "maintenance_margin_requirement",
                "shortable", "easy_to_borrow", "fractionable", "attributes"
            ]

            for attr in expected_attrs:
                assert hasattr(result, attr), f"Missing expected attribute: {attr}"