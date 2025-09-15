import pytest

from tests.mocks.adapters.mock_stream_adapter import MockStreamAdapter


@pytest.fixture
def stream_adapter():
    adapter = MockStreamAdapter()
    yield adapter


class TestStreamAdapter:
    def test_get_stream(self, stream_adapter):
        result = pytest.run(stream_adapter.get_stream())
        assert result is not None
        assert isinstance(result, list)
        assert "stream_event_1" in result

    def test_get_stream_empty(self, stream_adapter):
        stream_adapter.set_return_empty(True)
        result = pytest.run(stream_adapter.get_stream())
        assert result == []
        stream_adapter.reset_return_empty()
