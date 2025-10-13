import pytest

from algo_royale.application.orders.order_generator import OrderGenerator
from tests.mocks.application.mock_portfolio_strategy_registry import (
    MockPortfolioStrategyRegistry,
)
from tests.mocks.application.mock_signal_generator import MockSignalGenerator
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def order_generator():
    generator = OrderGenerator(
        signal_generator=MockSignalGenerator(),
        portfolio_strategy_registry=MockPortfolioStrategyRegistry(),
        logger=MockLoggable(),
    )
    yield generator


def set_signal_generator_return_empty(order_generator: OrderGenerator, value: bool):
    order_generator.signal_generator.set_return_empty(value)


def set_portfolio_strategy_registry_return_empty(
    order_generator: OrderGenerator, value: bool
):
    order_generator.portfolio_strategy_registry.set_return_empty(value)


def reset_order_generator(order_generator: OrderGenerator):
    order_generator.signal_generator.reset()
    order_generator.portfolio_strategy_registry.reset()


@pytest.mark.asyncio
class TestOrderGenerator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_generator: OrderGenerator):
        yield
        reset_order_generator(order_generator)

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_async_unsubscribe_from_order_events_no_pubsub(self, order_generator):
        # Should handle gracefully if pubsub is missing
        await order_generator.async_unsubscribe_from_order_events("FAKE", None)

    @pytest.mark.asyncio
    async def test_async_restart_stream_success(self, order_generator):
        await order_generator.async_restart_stream(["AAPL"])

    @pytest.mark.asyncio
    async def test_async_restart_stream_exception(self, order_generator):
        set_portfolio_strategy_registry_return_empty(order_generator, True)
        await order_generator.async_restart_stream(["AAPL"])
        set_portfolio_strategy_registry_return_empty(order_generator, False)

    @pytest.mark.asyncio
    async def test_async_stop_success(self, order_generator):
        await order_generator._async_stop()

    @pytest.mark.asyncio
    async def test_async_stop_exception(self, order_generator):
        # Simulate by clearing signal_generator and pubsub_orders_map
        order_generator.signal_roster_subscriber = None
        order_generator.pubsub_orders_map.clear()
        order_generator.portfolio_strategy = None
        order_generator.signal_order_subscribers.clear()
        order_generator.symbols = set()
        await order_generator._async_stop()
