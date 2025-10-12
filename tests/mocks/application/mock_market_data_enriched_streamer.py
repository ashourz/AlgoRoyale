from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from tests.mocks.application.mock_feature_engineer import MockFeatureEngineer
from tests.mocks.application.mock_market_data_raw_streamer import (
    MockMarketDataRawStreamer,
)
from tests.mocks.mock_loggable import MockLoggable


class MockMarketDataEnrichedStreamer(MarketDataEnrichedStreamer):
    def __init__(self):
        super().__init__(
            feature_engineer=MockFeatureEngineer(),
            market_data_streamer=MockMarketDataRawStreamer(),
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def async_subscribe_to_enriched_data(
        self, symbols, callback, queue_size=1
    ) -> dict[str, AsyncSubscriber] | None:
        if self.return_empty:
            return {}
        else:
            return {
                symbol: AsyncSubscriber(event_type="enriched", callback=None)
                for symbol in symbols
            }

    async def async_unsubscribe(self, symbol_subscribers):
        return

    async def async_restart_stream(self, symbols):
        return
