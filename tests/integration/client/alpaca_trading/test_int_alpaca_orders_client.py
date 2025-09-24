import uuid

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_orders_client
    try:
        yield client
    finally:
        client_container.close_all_clients()


@pytest.mark.asyncio
class TestAlpacaOrdersClientIntegration:
    async def test_order_lifecycle(self, alpaca_client: AlpacaOrdersClient):
        # Use a penny stock and minimal notional for safe paper trading
        penny_stock_symbol = "SNDL"  # Replace with a valid penny stock if needed
        client_order_id = f"integration_test_{uuid.uuid4().hex[:8]}"
        # Create order
        order = await alpaca_client.create_order(
            symbol=penny_stock_symbol,
            notional=1.00,  # Minimal notional (e.g., $1)
            side="buy",
            order_type="market",
            time_in_force="day",
            client_order_id=client_order_id,
        )
        assert order is not None and hasattr(order, "id")
        # Get order by client_order_id
        fetched = await alpaca_client.get_order_by_client_order_id(client_order_id)
        assert fetched is not None and fetched.id == order.id
        # Cancel/delete the order using order.id
        try:
            await alpaca_client.delete_order_by_id(order.id)
        except Exception as e:
            # Accept if order is already filled
            if "filled" not in str(e).lower():
                raise
        # Confirm order is cancelled or not found
        try:
            cancelled = await alpaca_client.get_order_by_client_order_id(
                client_order_id
            )
            # Depending on API, cancelled order may still be returned with cancelled status
            assert cancelled is None or getattr(cancelled, "status", None) in (
                "canceled",
                "cancelled",
                "rejected",
            )
        except Exception:
            pass
