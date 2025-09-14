# src: tests/integration/client/test_alpaca_account_client.py


from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import (
    AlpacaAssetsClient,
)
from algo_royale.clients.alpaca.exceptions import AlpacaAssetNotFoundException
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaAssetsClient(
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
    # Patch fetch_assets to return a fake list of Asset objects
    fake_asset = Asset(
        id="asset_id",
        class_="us_equity",
        exchange="NASDAQ",
        symbol="AAPL",
        name="Apple Inc.",
        status="active",
        tradable=True,
        marginable=True,
        maintenance_margin_requirement=25,
        shortable=True,
        easy_to_borrow=True,
        fractionable=True,
        attributes=[],
    )
    monkeypatch.setattr(client, "fetch_assets", AsyncMock(return_value=[fake_asset]))
    monkeypatch.setattr(
        client, "fetch_asset_by_symbol_or_id", AsyncMock(return_value=fake_asset)
    )
    yield client
    await client.aclose()


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
                "id",
                "class_",
                "exchange",
                "symbol",
                "name",
                "status",
                "tradable",
                "marginable",
                "maintenance_margin_requirement",
                "shortable",
                "easy_to_borrow",
                "fractionable",
                "attributes",
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
                symbol_or_asset_id=symbol
            )
            assert result is not None
            assert isinstance(result, Asset)

            expected_attrs = [
                "id",
                "class_",
                "exchange",
                "symbol",
                "name",
                "status",
                "tradable",
                "marginable",
                "maintenance_margin_requirement",
                "shortable",
                "easy_to_borrow",
                "fractionable",
                "attributes",
            ]

            for attr in expected_attrs:
                assert hasattr(result, attr), f"Missing expected attribute: {attr}"
        except AlpacaAssetNotFoundException:
            return None
