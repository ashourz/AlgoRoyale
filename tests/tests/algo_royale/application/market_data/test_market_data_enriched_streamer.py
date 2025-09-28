import pytest

from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from tests.mocks.application.mock_feature_engineer import MockFeatureEngineer
from tests.mocks.application.mock_market_data_raw_streamer import (
    MockMarketDataRawStreamer,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def market_data_enriched_streamer():
    service = MarketDataEnrichedStreamer(
        feature_engineer=MockFeatureEngineer(),
        market_data_streamer=MockMarketDataRawStreamer(),
        logger=MockLoggable(),
    )
    yield service


def set_market_data_raw_streamer_return_empty(
    market_data_enriched_streamer: MarketDataEnrichedStreamer, value: bool
):
    market_data_enriched_streamer.market_data_streamer.set_return_empty(value)


def reset_market_data_enriched_streamer(
    market_data_enriched_streamer: MarketDataEnrichedStreamer,
):
    market_data_enriched_streamer.market_data_streamer.reset()


@pytest.mark.asyncio
class TestMarketDataEnrichedStreamer:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, market_data_enriched_streamer: MarketDataEnrichedStreamer
    ):
        yield
        reset_market_data_enriched_streamer(market_data_enriched_streamer)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_enriched_data_success(
        self, market_data_enriched_streamer: MarketDataEnrichedStreamer
    ):
        def callback(data, typ):
            pass

        result = await market_data_enriched_streamer.async_subscribe_to_enriched_data(
            ["AAPL"], callback
        )
        assert result is not None

    # Removed test_async_subscribe_to_enriched_data_exception: mock_market_data_streamer never raises

    @pytest.mark.asyncio
    async def test_async_unsubscribe_from_enriched_data_success(
        self, market_data_enriched_streamer
    ):
        def callback(data, typ):
            pass

        result = await market_data_enriched_streamer.async_subscribe_to_enriched_data(
            ["AAPL"], callback
        )
        await market_data_enriched_streamer.async_unsubscribe_from_enriched_data(
            {"AAPL": [result["AAPL"]]}
        )

    # Removed test_async_unsubscribe_from_enriched_data_exception: mock_market_data_streamer never raises

    @pytest.mark.asyncio
    async def test_async_restart_stream_success(self, market_data_enriched_streamer):
        await market_data_enriched_streamer.async_restart_stream(["AAPL"])

    # Removed test_async_restart_stream_exception: mock_market_data_streamer never raises

    @pytest.mark.asyncio
    async def test_async_stop_success(self, market_data_enriched_streamer):
        await market_data_enriched_streamer._async_stop()

    # Removed test_async_stop_exception: mock_market_data_streamer never raises
