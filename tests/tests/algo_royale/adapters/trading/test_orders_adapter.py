import pytest

from algo_royale.adapters.trading.orders_adapter import OrdersAdapter
from tests.mocks.adapters.mock_orders_adapter import MockOrdersAdapter


@pytest.fixture
def orders_adapter():
    adapter = MockOrdersAdapter()
    yield adapter


@pytest.mark.asyncio
class TestOrdersAdapter:
    async def test_create_order(self, orders_adapter: OrdersAdapter):
        result = await orders_adapter.create_order(
            symbol="AAPL", qty=1, side=None, order_type=None, time_in_force=None
        )
        assert result is not None
        assert hasattr(result, "id")

    async def test_get_all_orders(self, orders_adapter: OrdersAdapter):
        result = await orders_adapter.get_all_orders()
        assert result is not None
        assert hasattr(result, "orders")
        assert isinstance(result.orders, list)

    async def test_get_order_by_client_order_id(self, orders_adapter: OrdersAdapter):
        result = await orders_adapter.get_order_by_client_order_id("client_order_id")
        assert result is not None
        assert hasattr(result, "id")

    async def test_replace_order_by_client_order_id(
        self, orders_adapter: OrdersAdapter
    ):
        result = await orders_adapter.replace_order_by_client_order_id(
            "client_order_id", qty=2
        )
        assert result is not None
        assert hasattr(result, "id")

    async def test_delete_order_by_client_order_id(self, orders_adapter: OrdersAdapter):
        # Should not raise
        await orders_adapter.delete_order_by_order_id("client_order_id")

    async def test_delete_all_orders(self, orders_adapter: OrdersAdapter):
        result = await orders_adapter.delete_all_orders()
        assert result is not None

    async def test_create_order_empty(self, orders_adapter: OrdersAdapter):
        orders_adapter.set_return_empty(True)
        result = await orders_adapter.create_order(
            symbol="AAPL", qty=1, side=None, order_type=None, time_in_force=None
        )
        assert result is None or result == []
        orders_adapter.reset_return_empty()

    async def test_get_all_orders_empty(self, orders_adapter: OrdersAdapter):
        orders_adapter.set_return_empty(True)
        result = await orders_adapter.get_all_orders()
        assert result is None or (hasattr(result, "orders") and result.orders == [])
        orders_adapter.reset_return_empty()

    async def test_get_order_by_client_order_id_empty(
        self, orders_adapter: OrdersAdapter
    ):
        orders_adapter.set_return_empty(True)
        result = await orders_adapter.get_order_by_client_order_id("client_order_id")
        assert result is None
        orders_adapter.reset_return_empty()

    async def test_replace_order_by_client_order_id_empty(
        self, orders_adapter: OrdersAdapter
    ):
        orders_adapter.set_return_empty(True)
        result = await orders_adapter.replace_order_by_client_order_id(
            "client_order_id", qty=2
        )
        assert result is None
        orders_adapter.reset_return_empty()
