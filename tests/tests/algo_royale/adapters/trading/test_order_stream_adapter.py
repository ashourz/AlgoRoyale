import pytest

from tests.mocks.adapters.mock_order_stream_adapter import MockOrderStreamAdapter


@pytest.fixture
def order_stream_adapter():
    adapter = MockOrderStreamAdapter()
    yield adapter


@pytest.mark.asyncio
class TestOrderStreamAdapter:
    async def test_subscribe_orders(self, order_stream_adapter):
        result = await order_stream_adapter.subscribe_orders()
        assert result is None or result == []

    async def test_unsubscribe_orders(self, order_stream_adapter):
        result = await order_stream_adapter.unsubscribe_orders()
        assert result is None or result == []

    async def test_on_start_stream(self, order_stream_adapter):
        result = await order_stream_adapter._on_start_stream()
        assert result is None
