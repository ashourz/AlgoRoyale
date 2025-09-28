from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from tests.mocks.application.mock_market_data_enriched_streamer import (
    MockMarketDataEnrichedStreamer,
)
from tests.mocks.application.mock_signal_strategy_registry import (
    MockSignalStrategyRegistry,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSignalGenerator(SignalGenerator):
    def __init__(self):
        super().__init__(
            enriched_data_streamer=MockMarketDataEnrichedStreamer(),
            strategy_registry=MockSignalStrategyRegistry(),
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def async_subscribe_to_signals(
        self, symbols, callback, queue_size=1
    ) -> AsyncSubscriber | None:
        if self.return_empty:
            return None
        else:
            return AsyncSubscriber(event_type="signal", callback=None)

    async def async_unsubscribe_from_signals(self, subscriber):
        return

    async def async_restart_stream(self):
        return
