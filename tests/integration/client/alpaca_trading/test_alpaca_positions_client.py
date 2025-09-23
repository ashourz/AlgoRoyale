import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import (
    AlpacaPositionsClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_position import Position


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_positions_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaPositionsClientIntegration:
    async def test_get_positions(self, alpaca_client: AlpacaPositionsClient):
        response = await alpaca_client.get_positions()
        assert response is not None
        assert isinstance(response, list)
        if response:
            assert isinstance(response[0], Position)

    async def test_get_position_by_symbol(self, alpaca_client: AlpacaPositionsClient):
        response = await alpaca_client.get_position_by_symbol("AAPL")
        assert response is None or isinstance(response, Position)
