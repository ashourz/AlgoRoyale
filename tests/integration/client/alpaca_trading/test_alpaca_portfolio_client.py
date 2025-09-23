import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import (
    AlpacaPortfolioClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_portfolio_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaPortfolioClientIntegration:
    async def test_get_portfolio_performance(
        self, alpaca_client: AlpacaPortfolioClient
    ):
        response = await alpaca_client.fetch_portfolio_history()
        assert response is not None
        assert isinstance(response, PortfolioPerformance)
