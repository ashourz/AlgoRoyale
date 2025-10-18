import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import (
    AlpacaClockClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.utils.application_env import ApplicationEnv
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
        await client_container.async_close_all_clients()


@pytest.mark.asyncio
class TestAlpacaClockClientIntegration:
    async def test_get_clock(self, alpaca_client: AlpacaClockClient):
        response = await alpaca_client.fetch_clock()
        assert response is not None
        assert isinstance(response, Clock)
