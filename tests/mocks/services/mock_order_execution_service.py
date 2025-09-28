from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.orders_execution_service import OrderExecutionService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_generator_service import MockOrderGeneratorService
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService


class MockOrderExecutionService(OrderExecutionService):
    def __init__(self):
        super().__init__(
            symbol_hold_service=MockSymbolHoldService(),
            ledger_service=MockLedgerService(),
            order_generator_service=MockOrderGeneratorService(),  # noqa: F821
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def start(self, symbols: list[str]):
        return (
            {}
            if self.return_empty
            else {
                symbol: AsyncSubscriber(event_type="order", callback=None)
                for symbol in symbols
            }
        )

    async def stop(self, symbol_subscribers: dict[str, list[AsyncSubscriber]]) -> bool:
        return not self.return_empty

    def update_executor_status(self, status: bool):
        return
