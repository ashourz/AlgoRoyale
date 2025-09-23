import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_order import Order


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_orders_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaOrdersClientIntegration:
    async def test_get_orders(self, alpaca_client: AlpacaOrdersClient):
        response = await alpaca_client.get_orders()
        assert response is not None
        assert isinstance(response, list)
        if response:
            assert isinstance(response[0], Order)

    async def test_get_order_by_id(self, alpaca_client: AlpacaOrdersClient):
        # Replace 'order_id' with a valid order id for a real test
        order_id = "test_order_id"
        response = await alpaca_client.get_order_by_id(order_id)
        assert response is None or isinstance(response, Order)
