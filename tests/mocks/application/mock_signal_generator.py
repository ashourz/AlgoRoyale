import inspect

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
    # Store callbacks for each symbol to simulate signal/order flow
    import asyncio
    import inspect

    async def _simulate_signal_and_order(self, symbols, callback, roster=None):
        # If a custom roster is provided, use it; otherwise, send empty signals
        from algo_royale.application.signals.signals_data_payload import (
            SignalDataPayload,
        )

        if roster is not None:
            if inspect.iscoroutinefunction(callback):
                await callback(roster)
            else:
                callback(roster)
        else:
            for symbol in symbols:
                payload = SignalDataPayload(signals={}, price_data={})
                if inspect.iscoroutinefunction(callback):
                    await callback({symbol: payload})
                else:
                    callback({symbol: payload})

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
        self, symbols, callback, queue_size=1, roster=None
    ) -> tuple[list[str], AsyncSubscriber | None]:
        if self.return_empty:
            return ([], None)
        # Simulate signal processing and order generation for test symbols
        await self._simulate_signal_and_order(symbols, callback, roster=roster)
        return (symbols, AsyncSubscriber(event_type="signal", callback=callback))

    async def async_unsubscribe_from_signals(self, subscriber):
        return

    async def async_restart_stream(self):
        return
