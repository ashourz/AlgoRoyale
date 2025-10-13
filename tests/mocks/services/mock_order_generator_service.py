from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.order_generator_service import OrderGeneratorService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_order_event_service import MockOrderEventService
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService


class MockOrderGeneratorService(OrderGeneratorService):
    def __init__(self):
        super().__init__(
            order_generator=MockOrderEventService(),
            symbol_hold_service=MockSymbolHoldService(),
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def subscribe_to_symbol_orders(
        self, symbols: list[str], callback
    ) -> dict[str, AsyncSubscriber] | None:
        return (
            {}
            if self.return_empty
            else {
                symbol: AsyncSubscriber(event_type="order", callback=None)
                for symbol in symbols
            }
        )

    async def unsubscribe_from_symbol_orders(self, symbols: dict[str, AsyncSubscriber]):
        return
