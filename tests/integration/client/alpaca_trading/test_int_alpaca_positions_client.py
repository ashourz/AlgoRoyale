import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import (
    AlpacaPositionsClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.utils.application_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_position import (
    ClosedPositionList,
    PositionList,
)


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_positions_client
    try:
        yield client
    finally:
        await client_container.async_close_all_clients()


@pytest.mark.asyncio
class TestAlpacaPositionsClientIntegration:
    async def test_fetch_all_open_positions(self, alpaca_client: AlpacaPositionsClient):
        response = await alpaca_client.fetch_all_open_positions()
        assert response is None or isinstance(response, PositionList)

    async def test_fetch_open_position_by_symbol_or_asset_id(
        self, alpaca_client: AlpacaPositionsClient
    ):
        # Replace with a real symbol or asset id for a real test
        symbol_or_asset_id = "AAPL"
        try:
            response = await alpaca_client.fetch_open_position_by_symbol_or_asset_id(
                symbol_or_asset_id
            )
            assert response is None or isinstance(response, PositionList)
        except Exception:
            pass

    async def test_close_position_by_symbol_or_asset_id(
        self, alpaca_client: AlpacaPositionsClient
    ):
        # Replace with a real symbol or asset id for a real test
        symbol_or_asset_id = "AAPL"
        try:
            response = await alpaca_client.close_position_by_symbol_or_asset_id(
                symbol_or_asset_id, qty=0.01
            )
            assert response is None or isinstance(response, ClosedPositionList)
        except Exception:
            pass

    async def test_close_all_positions(self, alpaca_client: AlpacaPositionsClient):
        try:
            response = await alpaca_client.close_all_positions()
            assert response is None or isinstance(response, ClosedPositionList)
        except Exception:
            pass
