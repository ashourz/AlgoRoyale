import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_accounts_client import (
    AlpacaAccountClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_account import (
    Account,
    AccountActivities,
    AccountConfiguration,
)


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_account_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaAccountClientIntegration:
    async def test_get_account(self, alpaca_client: AlpacaAccountClient):
        response = await alpaca_client.get_account()
        assert response is not None
        assert isinstance(response, Account)

    async def test_get_account_configuration(self, alpaca_client: AlpacaAccountClient):
        response = await alpaca_client.get_account_configuration()
        assert response is not None
        assert isinstance(response, AccountConfiguration)

    async def test_get_account_activities(self, alpaca_client: AlpacaAccountClient):
        response = await alpaca_client.get_account_activities()
        assert response is not None
        assert isinstance(response, AccountActivities)
