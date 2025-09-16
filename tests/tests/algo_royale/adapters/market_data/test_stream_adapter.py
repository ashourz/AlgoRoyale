import pytest

from tests.mocks.adapters.mock_stream_adapter import MockStreamAdapter


@pytest.fixture
def stream_adapter():
    adapter = MockStreamAdapter()
    yield adapter


@pytest.mark.asyncio
class TestStreamAdapter:
    async def test_get_stream(self, stream_adapter):
        result = await stream_adapter.get_stream()
        assert result is not None
        assert isinstance(result, list)
        assert "stream_event_1" in result

    async def test_get_stream_empty(self, stream_adapter):
        stream_adapter.set_return_empty(True)
        result = await stream_adapter.get_stream()
        assert result == []
        stream_adapter.reset_return_empty()
