import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import (
    AlpacaClockClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_clock import Clock


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_clock_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaClockClientIntegration:
    async def test_get_clock(self, alpaca_client: AlpacaClockClient):
        response = await alpaca_client.get_clock()
        assert response is not None
        assert isinstance(response, Clock)
