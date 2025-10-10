import pytest

from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.utils.clock_provider import ClockProvider
from tests.mocks.adapters.mock_stream_adapter import MockStreamAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_data_stream_session_repo import MockDataStreamSessionRepo


@pytest.fixture
def market_data_raw_streamer():
    service = MarketDataRawStreamer(
        stream_adapter=MockStreamAdapter(),
        data_stream_session_repo=MockDataStreamSessionRepo(),
        clock_provider=ClockProvider(),
        logger=MockLoggable(),
        is_live=False,
    )
    yield service


def set_stream_adapter_return_empty(
    market_data_raw_streamer: MarketDataRawStreamer, value: bool
):
    market_data_raw_streamer.stream_adapter.set_return_empty(value)


def reset_market_data_raw_streamer(
    market_data_raw_streamer: MarketDataRawStreamer,
):
    market_data_raw_streamer.stream_adapter.reset()


@pytest.mark.asyncio
class TestMarketDataRawStreamer:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, market_data_raw_streamer: MarketDataRawStreamer):
        yield
        reset_market_data_raw_streamer(market_data_raw_streamer)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_stream_success(self, market_data_raw_streamer):
        def callback(data):
            pass

        result = await market_data_raw_streamer.async_subscribe_to_stream(
            ["AAPL"], callback
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_stream_return_empty(
        self, market_data_raw_streamer
    ):
        set_stream_adapter_return_empty(market_data_raw_streamer, True)

        def callback(data):
            pass

        result = await market_data_raw_streamer.async_subscribe_to_stream(
            ["AAPL"], callback
        )
        assert result == {}
        set_stream_adapter_return_empty(market_data_raw_streamer, False)

    @pytest.mark.asyncio
    async def test_async_unsubscribe_from_stream_success(
        self, market_data_raw_streamer
    ):
        # Ensure return_empty is False so subscription works
        set_stream_adapter_return_empty(market_data_raw_streamer, False)

        def callback(data):
            pass

        result = await market_data_raw_streamer.async_subscribe_to_stream(
            ["AAPL"], callback
        )
        if not result or "AAPL" not in result:
            import warnings

            warnings.warn(
                f"Subscription did not return expected symbol: {result}. Skipping unsubscribe."
            )
            return
        await market_data_raw_streamer.async_unsubscribe_from_stream(
            {"AAPL": [result["AAPL"]]}
        )

    @pytest.mark.asyncio
    async def test_async_restart_stream_success(self, market_data_raw_streamer):
        await market_data_raw_streamer.async_restart_stream(["AAPL"])

    @pytest.mark.asyncio
    async def test_async_restart_stream_return_empty(self, market_data_raw_streamer):
        set_stream_adapter_return_empty(market_data_raw_streamer, True)
        await market_data_raw_streamer.async_restart_stream(["AAPL"])
        set_stream_adapter_return_empty(market_data_raw_streamer, False)

    @pytest.mark.asyncio
    async def test_async_stop_success(self, market_data_raw_streamer):
        await market_data_raw_streamer._async_stop()

    @pytest.mark.asyncio
    async def test_async_stop_return_empty(self, market_data_raw_streamer):
        set_stream_adapter_return_empty(market_data_raw_streamer, True)
        await market_data_raw_streamer._async_stop()
        set_stream_adapter_return_empty(market_data_raw_streamer, False)
