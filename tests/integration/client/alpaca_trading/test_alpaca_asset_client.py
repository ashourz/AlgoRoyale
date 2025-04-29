# src: tests/integration/client/test_alpaca_account_client.py

import logging
from the_risk_is_not_enough.client.exceptions import AlpacaAssetNotFoundException
import pytest
from the_risk_is_not_enough.client.alpaca_trading.alpaca_assets_client import AlpacaAssetsClient
from models.alpaca_trading.alpaca_asset import Asset

from logger.log_config import LoggerType, get_logger

# Set up logging (prints to console)
logger = get_logger(LoggerType.INTEGRATION)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaAssetsClient()

@pytest.mark.asyncio
class TestAlpacaAssetClientIntegration:
    
    def test_fetch_assets(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""
        try:
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
        except AlpacaAssetNotFoundException:
            return None
                
    def test_fetch_asset_by_symbol_or_id(self, alpaca_client):
        """Test fetching asset data from Alpaca's live endpoint."""
        symbol = "AAPL"
        try:
            result = alpaca_client.fetch_asset_by_symbol_or_id(
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
