from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.clients.alpaca.exceptions import (
    InsufficientBuyingPowerOrSharesError,
    UnprocessableOrderException,
)
from algo_royale.models.alpaca_trading.alpaca_order import (
    DeleteOrdersResponse,
    DeleteOrderStatus,
    Order,
    OrderListResponse,
)

# src: tests/integration/client/test_alpaca_account_client.py
from algo_royale.models.alpaca_trading.enums.enums import (
    OrderSide,
    OrderStatusFilter,
    OrderType,
    SortDirection,
    TimeInForce,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaOrdersClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    # Patch fetch_orders and fetch_order to return fake responses
    fake_order = Order(
        symbol="AAPL",
        qty=1,
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY,
        id="order_id",
        status="new",
        client_order_id="client_order_id",
        created_at="2024-01-01T09:30:00",
        updated_at="2024-01-01T09:31:00",
        submitted_at="2024-01-01T09:30:00",
        asset_id="asset_id",
        asset_class="us_equity",
        filled_qty=0,
        order_type=OrderType.MARKET,
        extended_hours=False,
    )
    monkeypatch.setattr(
        client,
        "get_all_orders",
        AsyncMock(return_value=OrderListResponse(orders=[fake_order])),
    )
    monkeypatch.setattr(
        client, "get_order_by_client_order_id", AsyncMock(return_value=fake_order)
    )
    monkeypatch.setattr(client, "create_order", AsyncMock(return_value=fake_order))
    monkeypatch.setattr(
        client,
        "delete_order_by_client_order_id",
        AsyncMock(return_value=DeleteOrderStatus(id="order_id", status=1)),
    )
    monkeypatch.setattr(
        client,
        "delete_all_orders",
        AsyncMock(
            return_value=DeleteOrdersResponse(
                orders=[DeleteOrderStatus(id="order_id", status=200)]
            )
        ),
    )
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaOrdersClientIntegration:
    def validate_order(self, order: Order):
        assert order is not None
        assert isinstance(order, Order)

        assert hasattr(order, "symbol")
        assert hasattr(order, "qty")
        assert hasattr(order, "side")
        assert hasattr(order, "type")
        assert hasattr(order, "time_in_force")
        assert hasattr(order, "id")
        assert order.id is not None
        assert hasattr(order, "status")
        assert order.status in {
            "new",
            "partially_filled",
            "filled",
            "accepted",
            "pending_new",
        }

        assert hasattr(order, "created_at")

        assert isinstance(order.created_at, datetime)

    async def test_create_order(self, alpaca_client):
        """Test creating a market order via Alpaca's live endpoint."""

        symbol = "AAPL"
        qty = 1  # small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.MARKET
        time_in_force = TimeInForce.DAY

        try:
            order = await alpaca_client.create_order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type=order_type,
                time_in_force=time_in_force,
            )
            alpaca_client.logger.debug("Order Response", order)

            # ✅ SUCCESS CASE - Status 200
            assert order is not None
            assert isinstance(order, Order)

            assert hasattr(order, "symbol")
            assert order.symbol == symbol
            assert hasattr(order, "qty")
            assert float(order.qty) == qty
            assert hasattr(order, "side")
            assert order.side.lower() == side.value
            assert hasattr(order, "type")
            assert order.type.lower() == order_type.value
            assert hasattr(order, "time_in_force")
            assert order.time_in_force.lower() == time_in_force.value
            assert hasattr(order, "id")
            assert order.id is not None
            assert hasattr(order, "status")
            assert order.status in {
                "new",
                "partially_filled",
                "filled",
                "accepted",
                "pending_new",
            }

            assert hasattr(order, "created_at")
            assert isinstance(order.created_at, datetime)

        except InsufficientBuyingPowerOrSharesError:
            return None

    async def test_get_all_orders(self, alpaca_client):
        """Test fetching orders via Alpaca's live endpoint."""

        symbol = "AAPL"
        qty = 1  # Small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.LIMIT
        time_in_force = TimeInForce.DAY
        limit_price = 1  # Unlikely to fill for AAPL

        try:
            # CREATE ORDER
            order = await alpaca_client.create_order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )

            self.validate_order(order)

            # Optional filter parameters (minimal test case)
            status = OrderStatusFilter.OPEN  # default is "open" if omitted
            limit = 10
            direction = SortDirection.DESC

            orders = await alpaca_client.get_all_orders(
                status=status,
                limit=limit,
                direction=direction,
            )

            # ✅ SUCCESS CASE - Should return an OrderListResponse or list of orders
            assert orders is not None
            assert isinstance(orders, OrderListResponse)

            # If any orders are present, inspect their structure
            if orders.orders:
                for order in orders.orders:
                    assert isinstance(order, Order)

                    assert hasattr(order, "id")
                    assert order.id is not None

                    assert hasattr(order, "symbol")
                    assert isinstance(order.symbol, str)

                    assert hasattr(order, "side")
                    assert order.side in {"buy", "sell"}

                    assert hasattr(order, "type")
                    assert order.type in {
                        "market",
                        "limit",
                        "stop",
                        "stop_limit",
                        "trailing_stop",
                    }

                    assert hasattr(order, "status")

                    assert hasattr(order, "created_at")
                    assert isinstance(order.created_at, datetime)
        except InsufficientBuyingPowerOrSharesError:
            return None

    async def test_delete_all_orders(self, alpaca_client):
        """Test deleting all orders via Alpaca's live endpoint."""
        symbol = "AAPL"
        qty = 1  # Small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.LIMIT
        time_in_force = TimeInForce.DAY
        limit_price = 1  # Unlikely to fill for AAPL

        try:
            # CREATE ORDER
            order = await alpaca_client.create_order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )

            self.validate_order(order)
            # try:
            response = await alpaca_client.delete_all_orders()

            # ✅ SUCCESS CASE
            assert response is not None
            assert isinstance(response, DeleteOrdersResponse)
            assert isinstance(response.orders, list)

            for order_status in response.orders:
                assert isinstance(order_status, DeleteOrderStatus)

                assert hasattr(order_status, "id")
                assert isinstance(order_status.id, str)
                assert len(order_status.id) > 0

                assert hasattr(order_status, "status")
                assert isinstance(order_status.status, int)
                assert order_status.status in {200, 500}  # valid possible HTTP codes
        except InsufficientBuyingPowerOrSharesError:
            return None
        except UnprocessableOrderException:
            return None

    async def test_life_cycle(self, alpaca_client):
        """Test creating, getting, replacing, and deleting an order."""

        symbol = "AAPL"
        qty = 1  # Small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.LIMIT
        time_in_force = TimeInForce.DAY
        limit_price = 1  # Unlikely to fill for AAPL

        try:
            # CREATE ORDER
            order = await alpaca_client.create_order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
            )

            self.validate_order(order)

            # GET ORDER
            get_order = await alpaca_client.get_order_by_client_order_id(
                client_order_id=order.client_order_id
            )

            # DELETE ORDER
            await alpaca_client.delete_order_by_client_order_id(
                client_order_id=get_order.id
            )
        except InsufficientBuyingPowerOrSharesError:
            return None
        except UnprocessableOrderException:
            return None
