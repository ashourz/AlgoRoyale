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
            stream_adapter=MockStreamAdapter(),
            logger=MockLoggable(),
            is_live=False,
        )
        self.return_empty = False
        self.subscribers = {}  # symbol -> list of AsyncSubscriber

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
        result = {}
        for symbol in symbols:
            subscriber = AsyncSubscriber(event_type="raw", callback=callback)
            self.subscribers.setdefault(symbol, []).append(subscriber)
            result[symbol] = subscriber
        return result

    async def async_unsubscribe_from_stream(self, symbol, async_subscriber):
        # Remove the subscriber from the list for the symbol
        if symbol in self.subscribers:
            if async_subscriber in self.subscribers[symbol]:
                self.subscribers[symbol].remove(async_subscriber)
            if not self.subscribers[symbol]:
                del self.subscribers[symbol]
        return

    async def async_restart_stream(self, symbols: list[str]) -> bool:
        return
