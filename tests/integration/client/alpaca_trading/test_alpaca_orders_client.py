# src: tests/integration/client/test_alpaca_account_client.py

from datetime import datetime, timedelta
import logging
from uuid import uuid4
from algo_royale.client.alapaca_trading.alpaca_orders_client import AlpacaOrdersClient
from httpx import HTTPStatusError
from models.alpaca_trading.alpaca_order import DeleteOrderStatus, DeleteOrdersResponse, OrderListResponse, Order
from models.alpaca_trading.enums import OrderSide, OrderStatus, OrderStatusFilter, OrderType, SortDirection, TimeInForce
import pytest

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaOrdersClient()

@pytest.mark.asyncio
class TestAlpacaOrdersClientIntegration:
                
    def test_create_order(self, alpaca_client):
        """Test creating a market order via Alpaca's live endpoint."""

        symbol = "AAPL"
        qty = 1  # small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.MARKET
        time_in_force = TimeInForce.DAY

        try:
            order = alpaca_client.create_order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type=order_type,
                time_in_force=time_in_force
            )
            logger.debug("Order Response", order)

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
                "new", "partially_filled", "filled", "accepted", "pending_new"
            }

            assert hasattr(order, "created_at")
            assert isinstance(order.created_at, datetime)

        except HTTPStatusError as e:
            status_code = e.response.status_code
            response_text = e.response.text.lower()

            if status_code == 403:
                logger.debug("⚠️ Test skipped: 403 Forbidden - Reason: %s", response_text)
                assert any(
                    phrase in response_text
                    for phrase in ["forbidden", "buying power", "fractional trading is disabled"]
                )
                
            elif status_code == 422:
                logger.debug("⚠️ Test skipped: 422 Unprocessable Entity - Input error.")
                assert "unprocessable" in response_text or "parameter" in response_text

            else:
                # ❌ Unexpected error — fail the test
                pytest.fail(f"Unexpected HTTP {status_code}: {e.response.text}")
                
    def test_get_all_orders(self, alpaca_client):
        """Test fetching orders via Alpaca's live endpoint."""

        # Optional filter parameters (minimal test case)
        status = OrderStatusFilter.OPEN  # default is "open" if omitted
        limit = 10
        direction = SortDirection.DESC

        try:
            orders = alpaca_client.get_all_orders(
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
                    assert order.type in {"market", "limit", "stop", "stop_limit", "trailing_stop"}

                    assert hasattr(order, "status")

                    assert hasattr(order, "created_at")
                    assert isinstance(order.created_at, datetime)

        except HTTPStatusError as e:
            status_code = e.response.status_code
            response_text = e.response.text.lower()

            if status_code == 403:
                logger.debug("⚠️ Test skipped: 403 Forbidden - Reason: %s", response_text)
                assert "forbidden" in response_text or "permission" in response_text

            elif status_code == 422:
                logger.debug("⚠️ Test skipped: 422 Unprocessable Entity - Check input parameters.")
                assert "unprocessable" in response_text or "parameter" in response_text

            else:
                # ❌ Unexpected error — fail the test
                pytest.fail(f"Unexpected HTTP {status_code}: {e.response.text}")
                
    def test_delete_all_orders(self, alpaca_client):
        """Test deleting all orders via Alpaca's live endpoint."""

        try:
            response = alpaca_client.delete_all_orders()

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
                assert order_status.status in {207, 500}  # valid possible HTTP codes

        except HTTPStatusError as e:
            status_code = e.response.status_code
            response_text = e.response.text.lower()

            if status_code == 403:
                pytest.skip(f"Permission denied: {response_text}")
            elif status_code == 422:
                pytest.skip(f"Unprocessable request: {response_text}")
            else:
                # ❌ Unexpected error — fail the test
                pytest.fail(f"Unexpected HTTP {status_code}: {e.response.text}")
                
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
            "new", "partially_filled", "filled", "accepted", "pending_new"
        }

        assert hasattr(order, "created_at")
        assert isinstance(order.created_at, datetime)
    
    def test_life_cycle(self, alpaca_client):
        """Test creating, getting, replacing, and deleting an order."""
        
        symbol = "AAPL"
        qty = 1  # Small amount for safe testing
        side = OrderSide.BUY
        order_type = OrderType.LIMIT
        time_in_force = TimeInForce.DAY
        limit_price = 1  # Unlikely to fill for AAPL

        
        # CREATE ORDER
        order = alpaca_client.create_order(
            symbol=symbol,
            qty=qty,
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            limit_price = limit_price
        )

        self.validate_order(order)
        
        # GET ORDER
        get_order = alpaca_client.get_order_by_client_order_id(
            client_order_id=order.client_order_id
        )
        
    
        # DELETE ORDER
        alpaca_client.delete_order_by_client_order_id(
            client_order_id=get_order.id
        )
