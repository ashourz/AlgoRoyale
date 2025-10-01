import pytest

from algo_royale.services.order_monitor_service import OrderMonitorService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_event_service import MockOrderEventService
from tests.mocks.services.mock_trades_service import MockTradesService


@pytest.fixture
def order_monitor_service():
    service = OrderMonitorService(
        ledger_service=MockLedgerService(),
        order_event_service=MockOrderEventService(),
        trades_service=MockTradesService(),
        clock_service=MockClockService(),
        logger=MockLoggable(),
    )
    yield service


@pytest.mark.asyncio
class TestOrderMonitorService:
    async def test_async_start_and_stop(self, order_monitor_service):
        await order_monitor_service.async_start()
        await order_monitor_service.async_stop()
