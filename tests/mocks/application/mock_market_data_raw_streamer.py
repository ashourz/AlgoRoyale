from typing import Any

from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from tests.mocks.adapters.mock_stream_adapter import MockStreamAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockMarketDataRawStreamer(MarketDataRawStreamer):
    """A mock market data raw streamer for testing purposes."""

    def __init__(self):
        super().__init__(
            stream_adapter=MockStreamAdapter(),  # Assuming a MockStreamAdapter exists
            logger=MockLoggable(),
            is_live=False,
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.stream_adapter.reset()
        self.return_empty = False

    async def async_subscribe_to_stream(
        self, symbols: list[str], callback: Any
    ) -> dict[str, AsyncSubscriber]:
        if self.return_empty:
            return {}
        else:
            return {
                symbol: AsyncSubscriber(event_type="raw", callback=None)
                for symbol in symbols
            }

    async def async_unsubscribe_from_stream(self, symbol_subscribers):
        return

    async def async_restart_stream(self, symbols: list[str]) -> bool:
        return
