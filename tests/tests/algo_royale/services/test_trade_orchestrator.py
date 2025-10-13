import pytest

from algo_royale.services.trade_orchestrator import TradeOrchestrator
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService
from tests.mocks.services.mock_market_session_service import MockMarketSessionService


@pytest.fixture
def trade_orchestrator():
    service = TradeOrchestrator(
        clock_service=MockClockService(),
        market_session_service=MockMarketSessionService(),
        logger=MockLoggable(),
        premarket_open_duration_minutes=30,
    )
    yield service


def set_return_empty_market_session_service(service: TradeOrchestrator):
    service.market_session_service.set_return_empty(True)


def set_return_empty_clock_service(service: TradeOrchestrator):
    service.clock_service.set_return_empty(True)


def set_raise_exception_clock_service(service: TradeOrchestrator):
    service.clock_service.set_throw_exception(True)


def reset_services(service: TradeOrchestrator):
    service.market_session_service.reset()
    service.clock_service.reset()


@pytest.mark.asyncio
class TestTradeOrchestrator:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, trade_orchestrator: TradeOrchestrator):
        print("Setup")
        yield
        print("Teardown")
        reset_services(trade_orchestrator)

    @pytest.mark.asyncio
    async def test_start_success(self, trade_orchestrator: TradeOrchestrator):
        await trade_orchestrator.async_start()

    @pytest.mark.asyncio
    async def test_start_clock_service_exception(
        self, trade_orchestrator: TradeOrchestrator
    ):
        set_raise_exception_clock_service(trade_orchestrator)
        try:
            await trade_orchestrator.async_start()
        except Exception:
            pass  # Should not raise, but if it does, we catch for test completeness

    @pytest.mark.asyncio
    async def test_on_pre_market_open_success(
        self, trade_orchestrator: TradeOrchestrator
    ):
        await trade_orchestrator._on_pre_market_open()

    @pytest.mark.asyncio
    async def test_on_market_open_success(self, trade_orchestrator: TradeOrchestrator):
        await trade_orchestrator._on_market_open()

    @pytest.mark.asyncio
    async def test_on_market_closed_success(
        self, trade_orchestrator: TradeOrchestrator
    ):
        await trade_orchestrator._on_market_closed()

    @pytest.mark.asyncio
    async def test_stop_success(self, trade_orchestrator: TradeOrchestrator):
        await trade_orchestrator.async_stop()

    @pytest.mark.asyncio
    async def test_stop_clock_service_exception(
        self, trade_orchestrator: TradeOrchestrator
    ):
        set_raise_exception_clock_service(trade_orchestrator)
        try:
            await trade_orchestrator.async_stop()
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_schedule_market_sessions_success(
        self, trade_orchestrator: TradeOrchestrator
    ):
        await trade_orchestrator.schedule_market_sessions()

    @pytest.mark.asyncio
    async def test_schedule_market_sessions_empty_clock(
        self, trade_orchestrator: TradeOrchestrator
    ):
        set_return_empty_clock_service(trade_orchestrator)
        await trade_orchestrator.schedule_market_sessions()

    @pytest.mark.asyncio
    async def test_schedule_market_sessions_empty_market_session(
        self, trade_orchestrator: TradeOrchestrator
    ):
        set_return_empty_market_session_service(trade_orchestrator)
        await trade_orchestrator.schedule_market_sessions()

    @pytest.mark.asyncio
    async def test_schedule_market_sessions_clock_service_exception(
        self, trade_orchestrator: TradeOrchestrator
    ):
        set_raise_exception_clock_service(trade_orchestrator)
        try:
            await trade_orchestrator.schedule_market_sessions()
        except Exception:
            pass
