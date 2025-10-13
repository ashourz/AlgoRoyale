import pytest

from tests.mocks.adapters.mock_stream_adapter import MockStreamAdapter


@pytest.fixture
def stream_adapter():
    adapter = MockStreamAdapter()
    yield adapter


@pytest.mark.asyncio
class TestStreamAdapter:
    def test_get_stream_symbols(self, stream_adapter):
        symbols = stream_adapter.get_stream_symbols()
        assert hasattr(symbols, "quotes")
        assert hasattr(symbols, "trades")
        assert hasattr(symbols, "bars")
        assert isinstance(symbols.quotes, list)

    @pytest.mark.asyncio
    async def test_async_start_stream(self, stream_adapter):
        # Should not raise, just test invocation
        await stream_adapter.async_start_stream(["AAPL", "GOOG"])

    @pytest.mark.asyncio
    async def test_async_add_symbols(self, stream_adapter):
        await stream_adapter.async_add_symbols(
            quotes=["AAPL"], trades=["GOOG"], bars=["MSFT"]
        )
        # No assertion, just ensure no exception

    @pytest.mark.asyncio
    async def test_async_remove_symbols(self, stream_adapter):
        await stream_adapter.async_remove_symbols(
            quotes=["AAPL"], trades=["GOOG"], bars=["MSFT"]
        )
        # No assertion, just ensure no exception

    @pytest.mark.asyncio
    async def test_async_stop_stream(self, stream_adapter):
        await stream_adapter.async_stop_stream()
        # No assertion, just ensure no exception
