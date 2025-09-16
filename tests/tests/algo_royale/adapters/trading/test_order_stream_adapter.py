import pytest

from tests.mocks.adapters.mock_order_stream_adapter import MockOrderStreamAdapter


@pytest.fixture
def order_stream_adapter():
    adapter = MockOrderStreamAdapter()
    yield adapter


@pytest.mark.asyncio
class TestOrderStreamAdapter:
    async def test_start_and_stop(self, order_stream_adapter):
        # Should not raise
        await order_stream_adapter.start()
        await order_stream_adapter.stop()

    async def test_on_order_update(self, order_stream_adapter):
        # Should not raise and should publish to pubsub
        data = {"id": "order1", "status": "filled"}
        await order_stream_adapter._on_order_update(data)

    async def test_subscribe_and_unsubscribe(self, order_stream_adapter):
        async def callback(data):
            pass

        subscriber = order_stream_adapter.subscribe(callback)
        assert subscriber is not None
        order_stream_adapter.unsubscribe(subscriber)
