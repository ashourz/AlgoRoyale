from algo_royale.application.orders.order_generator import OrderGenerator
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from tests.mocks.application.mock_portfolio_strategy_registry import (
    MockPortfolioStrategyRegistry,
)
from tests.mocks.application.mock_signal_generator import MockSignalGenerator
from tests.mocks.mock_loggable import MockLoggable


class MockOrderGenerator(OrderGenerator):
    def __init__(self):
        super().__init__(
            signal_generator=MockSignalGenerator(),
            portfolio_strategy_registry=MockPortfolioStrategyRegistry(),
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def async_subscribe_to_order_events(
        self, symbols, callback, queue_size=1
    ) -> dict[str, AsyncSubscriber] | None:
        if self.return_empty:
            return {}
        else:
            return {
                symbol: AsyncSubscriber(event_type="order", callback=None)
                for symbol in symbols
            }

    async def async_unsubscribe_from_order_events(self, symbol, async_subscriber):
        return

    async def async_restart_stream(self, symbols):
        return
