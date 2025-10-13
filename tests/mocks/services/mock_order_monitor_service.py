from algo_royale.services.order_monitor_service import OrderMonitorService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_event_service import MockOrderEventService
from tests.mocks.services.mock_trades_service import MockTradesService


class MockOrderMonitorService(OrderMonitorService):
    def __init__(self):
        super().__init__(
            trades_service=MockTradesService(),
            ledger_service=MockLedgerService(),
            order_event_service=MockOrderEventService(),
            clock_service=MockClockService(),
            logger=MockLoggable(),
        )
