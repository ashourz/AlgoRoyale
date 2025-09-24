# src: tests/integration/client/alpaca_market_data/test_alpaca_stream_client.py
import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_stream_client
    try:
        yield client
    finally:
        client_container.close_all_clients()


@pytest.mark.asyncio
class TestAlpacaStreamClientIntegration:
    async def test_stream(self, alpaca_client: AlpacaStreamClient):
        # This is a placeholder test. Actual streaming tests require event loop and message handling.
        # Here we just check that the client can be instantiated and stream method exists.
        assert hasattr(alpaca_client, "stream")
        assert callable(getattr(alpaca_client, "stream", None))

    async def test_remove_symbols(self, alpaca_client: AlpacaStreamClient):
        # Placeholder for trade subscription test
        assert hasattr(alpaca_client, "remove_symbols")
        assert callable(getattr(alpaca_client, "remove_symbols", None))

    async def test_stop_stream(self, alpaca_client: AlpacaStreamClient):
        # Placeholder for quote subscription test
        assert hasattr(alpaca_client, "stop")
        assert callable(getattr(alpaca_client, "stop", None))
