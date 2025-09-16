import pytest

from tests.mocks.adapters.mock_orders_adapter import MockOrdersAdapter


@pytest.fixture
def orders_adapter():
    adapter = MockOrdersAdapter()
    yield adapter


@pytest.mark.asyncio
class TestOrdersAdapter:
    async def test_get_orders(self, orders_adapter):
        result = await orders_adapter.get_orders()
        assert isinstance(result, list)
        assert all(hasattr(o, "id") for o in result)

    async def test_get_order_by_id(self, orders_adapter):
        result = await orders_adapter.get_order_by_id("order_id")
        assert result is not None
        assert hasattr(result, "id")

    async def test_get_orders_empty(self, orders_adapter):
        orders_adapter.set_return_empty(True)
        result = await orders_adapter.get_orders()
        assert result == []
        orders_adapter.reset_return_empty()
