import pytest

from tests.mocks.adapters.mock_order_stream_adapter import MockOrderStreamAdapter


@pytest.fixture
def order_stream_adapter():
    adapter = MockOrderStreamAdapter()
    yield adapter


class TestOrderStreamAdapter:
    def test_get_order_stream(self, order_stream_adapter):
        result = pytest.run(order_stream_adapter.get_order_stream())
        assert result is not None
        assert isinstance(result, list)
        assert "order_event_1" in result

    def test_get_order_stream_empty(self, order_stream_adapter):
        order_stream_adapter.set_return_empty(True)
        result = pytest.run(order_stream_adapter.get_order_stream())
        assert result == []
        order_stream_adapter.reset_return_empty()
