from algo_royale.application.utils.async_pubsub import AsyncSubscriber
import pytest

from algo_royale.application.signals.signal_generator import SignalGenerator
from tests.mocks.application.mock_market_data_enriched_streamer import (
    MockMarketDataEnrichedStreamer,
)
from tests.mocks.application.mock_signal_strategy_registry import (
    MockSignalStrategyRegistry,
)
from tests.mocks.mock_loggable import MockLoggable



@pytest.fixture
def signal_generator():
    generator = SignalGenerator(
        enriched_data_streamer=MockMarketDataEnrichedStreamer(),
        strategy_registry=MockSignalStrategyRegistry(),
        logger=MockLoggable(),
    )
    yield generator


def set_enriched_streamer_return_empty(signal_generator, value: bool):
    signal_generator.enriched_data_streamer.set_return_empty(value)


def set_strategy_registry_return_empty(signal_generator, value: bool):
    signal_generator.strategy_registry.set_return_empty(value)


def reset_signal_generator(signal_generator):
    signal_generator.enriched_data_streamer.reset()
    signal_generator.strategy_registry.reset()


@pytest.mark.asyncio
class TestSignalGenerator:
    @pytest.mark.asyncio
    async def test_async_subscribe_to_signals_return_empty(self, signal_generator: SignalGenerator):
        set_enriched_streamer_return_empty(signal_generator, True)

        def callback(roster):
            pass

        symbol_subscriber_tuple = await signal_generator.async_subscribe(["AAPL"], callback)
        subscriber = symbol_subscriber_tuple[1]

        assert isinstance(subscriber, AsyncSubscriber)
        set_enriched_streamer_return_empty(signal_generator, False)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_signals_exception(self, signal_generator: SignalGenerator):
        # Simulate exception by passing invalid symbols (should be handled gracefully)
        def callback(roster):
            pass

        symbol_subscriber_tuple = await signal_generator.async_subscribe([], callback)
        subscriber = symbol_subscriber_tuple[1]
        assert isinstance(subscriber, AsyncSubscriber)

    @pytest.mark.asyncio
    async def test_async_unsubscribe_from_signals_success(self, signal_generator: SignalGenerator):
        def callback(roster):
            pass

        symbol_subscriber_tuple = await signal_generator.async_subscribe(
            ["AAPL"], callback
        )
        subscriber = symbol_subscriber_tuple[1]
        await signal_generator.async_unsubscribe(subscriber)

    @pytest.mark.asyncio
    async def test_async_unsubscribe_from_signals_exception(self, signal_generator: SignalGenerator):
        # Simulate exception by passing None as subscriber
        await signal_generator.async_unsubscribe(None)

    @pytest.mark.asyncio
    async def test_async_stop_success(self, signal_generator: SignalGenerator):
        await signal_generator._async_stop()

    @pytest.mark.asyncio
    async def test_async_stop_exception(self, signal_generator: SignalGenerator):
        # Simulate by clearing internal state
        signal_generator.subscribers.clear()
        signal_generator.symbol_strategy_map.clear()
        signal_generator.symbol_async_subscriber_map.clear()
        await signal_generator._async_stop()

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, signal_generator: SignalGenerator):
        yield
        reset_signal_generator(signal_generator)
