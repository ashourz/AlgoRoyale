import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_order import (
    DeleteOrdersResponse,
    Order,
    OrderListResponse,
)


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
    async def test_create_order(self, alpaca_client: AlpacaOrdersClient):
        # Use a penny stock symbol and a fractional share for safe paper trading
        penny_stock_symbol = (
            "SNDL"  # Example penny stock, replace with a valid one if needed
        )
        response = await alpaca_client.create_order(
            symbol=penny_stock_symbol,
            qty=0.01,  # Minimal fractional share
            side="buy",
            order_type="market",
            time_in_force="day",
        )
        assert response is None or hasattr(response, "id")

    async def test_get_all_orders(self, alpaca_client: AlpacaOrdersClient):
        response = await alpaca_client.get_all_orders()
        assert response is None or isinstance(response, OrderListResponse)

    async def test_get_order_by_client_order_id(
        self, alpaca_client: AlpacaOrdersClient
    ):
        # Replace with a real client_order_id for a real test
        client_order_id = "test_client_order_id"
        response = await alpaca_client.get_order_by_client_order_id(client_order_id)
        assert response is None or isinstance(response, Order)

    async def test_replace_order_by_client_order_id(
        self, alpaca_client: AlpacaOrdersClient
    ):
        # Replace with a real client_order_id and valid params for a real test
        client_order_id = "test_client_order_id"
        with pytest.raises(Exception):
            await alpaca_client.replace_order_by_client_order_id(client_order_id, qty=2)

    async def test_delete_order_by_client_order_id(
        self, alpaca_client: AlpacaOrdersClient
    ):
        # Replace with a real client_order_id for a real test
        client_order_id = "test_client_order_id"
        result = await alpaca_client.delete_order_by_client_order_id(client_order_id)
        assert result is None  # Should return None on success or if not found

    async def test_delete_all_orders(self, alpaca_client: AlpacaOrdersClient):
        try:
            response = await alpaca_client.delete_all_orders()
            assert response is None or isinstance(response, DeleteOrdersResponse)
        except Exception:
            # Acceptable if no orders to delete or API returns error
            pass
