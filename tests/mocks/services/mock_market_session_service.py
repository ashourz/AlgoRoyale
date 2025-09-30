from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.market_session_service import MarketSessionService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_execution_service import MockOrderExecutionService
from tests.mocks.services.mock_order_monitor_service import MockOrderMonitorService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService
from tests.mocks.services.mock_symbol_service import MockSymbolService
from tests.mocks.services.mock_trades_service import MockTradesService


class MockMarketSessionService(MarketSessionService):
    def __init__(self):
        super().__init__(
            order_service=MockOrderService(),
            positions_service=MockPositionsService(),
            symbol_service=MockSymbolService(),
            symbol_hold_service=MockSymbolHoldService(),
            trade_service=MockTradesService(),
            ledger_service=MockLedgerService(),
            order_execution_service=MockOrderExecutionService(),
            order_monitor_service=MockOrderMonitorService(),
            clock_service=MockClockService(),
            logger=MockLoggable(),
        )
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False

    async def async_start_premarket(self):
        return

    async def async_start_market(self) -> dict[str, AsyncSubscriber] | None:
        if self.return_empty:
            return None
        return {
            symbol: AsyncSubscriber(event_type="mock_event", callback=lambda x: x)
            for symbol in ["AAPL", "GOOG"]
        }

    async def async_stop_market(self):
        return
