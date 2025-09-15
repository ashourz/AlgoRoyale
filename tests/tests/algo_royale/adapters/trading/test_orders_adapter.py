import pytest

from tests.mocks.adapters.mock_orders_adapter import MockOrdersAdapter


@pytest.fixture
def orders_adapter():
    adapter = MockOrdersAdapter()
    yield adapter


class TestOrdersAdapter:
    def test_get_orders(self, orders_adapter):
        result = pytest.run(orders_adapter.get_orders())
        assert result is not None
        assert isinstance(result, list)
        assert any("id" in o for o in result)

    def test_get_orders_empty(self, orders_adapter):
        orders_adapter.set_return_empty(True)
        result = pytest.run(orders_adapter.get_orders())
        assert result == []
        orders_adapter.reset_return_empty()
