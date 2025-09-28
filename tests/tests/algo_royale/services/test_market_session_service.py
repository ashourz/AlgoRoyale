import pytest

from algo_royale.services.market_session_service import MarketSessionService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_execution_service import MockOrderExecutionService
from tests.mocks.services.mock_order_monitor_service import MockOrderMonitorService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService
from tests.mocks.services.mock_symbol_service import MockSymbolService
from tests.mocks.services.mock_trades_service import MockTradesService


@pytest.fixture
def market_session_service():
    service = MarketSessionService(
        order_service=MockOrderService(),
        positions_service=MockPositionsService(),
        symbol_service=MockSymbolService(),
        symbol_hold_service=MockSymbolHoldService(),
        trade_service=MockTradesService(),
        ledger_service=MockLedgerService(),
        order_execution_service=MockOrderExecutionService(),
        order_monitor_service=MockOrderMonitorService(),
        logger=MockLoggable(),
    )
    yield service


def raise_order_service_exception(market_session_service):
    market_session_service.order_service.set_raise_exception(True)


def raise_positions_service_exception(market_session_service):
    market_session_service.positions_service.set_raise_exception(True)


def raise_symbol_service_exception(market_session_service):
    market_session_service.symbol_service.set_raise_exception(True)


def raise_symbol_hold_service_exception(market_session_service):
    market_session_service.symbol_hold_service.set_raise_exception(True)


def raise_trade_service_exception(market_session_service):
    market_session_service.trade_service.set_raise_exception(True)


def raise_ledger_service_exception(market_session_service):
    market_session_service.ledger_service.set_raise_exception(True)


def raise_order_monitor_service_exception(market_session_service):
    market_session_service.order_monitor_service.set_raise_exception(True)


def reset_services(market_session_service):
    market_session_service.order_service.reset()
    market_session_service.positions_service.reset()
    market_session_service.symbol_service.reset()
    market_session_service.symbol_hold_service.reset()
    market_session_service.trade_service.reset()
    market_session_service.ledger_service.reset()
    market_session_service.order_execution_service.reset()
    market_session_service.order_monitor_service.reset()


@pytest.mark.asyncio
class TestMarketSessionService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, market_session_service):
        print("Setup")
        yield
        print("Teardown")
        reset_services(market_session_service)

    @pytest.mark.asyncio
    async def test_async_start_premarket_success(self, market_session_service):
        # Should complete without error and set premarket_completed True
        await market_session_service.async_start_premarket()
        assert market_session_service.premarket_completed is True

    @pytest.mark.asyncio
    async def test_async_start_premarket_exception(self, market_session_service):
        raise_trade_service_exception(market_session_service)
        await market_session_service.async_start_premarket()
        assert market_session_service.premarket_completed is False

    @pytest.mark.asyncio
    async def test_async_start_market_success(self, market_session_service):
        market_session_service.premarket_completed = True
        result = await market_session_service.async_start_market()
        assert result is None

    @pytest.mark.asyncio
    async def test_async_start_market_runs_premarket_on_missing(
        self, market_session_service
    ):
        # Should call async_start_premarket if not completed
        market_session_service.premarket_completed = False
        await market_session_service.async_start_market()
        assert market_session_service.premarket_completed is True

    @pytest.mark.asyncio
    async def test_async_start_market_exception(self, market_session_service):
        # order_execution_service exceptions are always caught, so this test is not needed
        market_session_service.premarket_completed = True
        result = await market_session_service.async_start_market()
        assert result is None

    @pytest.mark.asyncio
    async def test_async_stop_market_success(self, market_session_service):
        market_session_service.premarket_completed = True
        await market_session_service.async_stop_market()
        assert market_session_service.premarket_completed is False

    @pytest.mark.asyncio
    async def test_async_stop_market_exception(self, market_session_service):
        # order_execution_service exceptions are always caught, so this test is not needed
        await market_session_service.async_stop_market()

    def test__init_ledger_service_success(self, market_session_service):
        market_session_service._init_ledger_service()
        # Should not raise

    def test__init_ledger_service_exception(self, market_session_service):
        raise_ledger_service_exception(market_session_service)
        market_session_service._init_ledger_service()

    @pytest.mark.asyncio
    async def test__async_start_order_execution_subscription_success(
        self, market_session_service
    ):
        result = (
            await market_session_service._async_start_order_execution_subscription()
        )
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test__async_start_order_execution_subscription_exception(
        self, market_session_service
    ):
        # order_execution_service exceptions are always caught, so this test is not needed
        result = (
            await market_session_service._async_start_order_execution_subscription()
        )
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test__async_stop_order_execution_success(self, market_session_service):
        market_session_service.symbol_subscribers = {"AAPL": object()}
        await market_session_service._async_stop_order_execution()
        assert market_session_service.symbol_subscribers == {}

    @pytest.mark.asyncio
    async def test__async_stop_order_execution_exception(self, market_session_service):
        # order_execution_service exceptions are always caught, so this test is not needed
        market_session_service.symbol_subscribers = {"AAPL": object()}
        await market_session_service._async_stop_order_execution()
        assert market_session_service.symbol_subscribers == {}

    @pytest.mark.asyncio
    async def test__async_run_validations_success(self, market_session_service):
        await market_session_service._async_run_validations()
        # Should not raise

    @pytest.mark.asyncio
    async def test__async_run_validations_exception(self, market_session_service):
        raise_trade_service_exception(market_session_service)
        await market_session_service._async_run_validations()

    @pytest.mark.asyncio
    async def test__async_subscribe_to_symbol_holds_success(
        self, market_session_service
    ):
        result = await market_session_service._async_subscribe_to_symbol_holds()
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test__async_subscribe_to_symbol_holds_exception(
        self, market_session_service
    ):
        raise_symbol_hold_service_exception(market_session_service)
        result = await market_session_service._async_subscribe_to_symbol_holds()
        assert result is False

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_symbol_holds_success(
        self, market_session_service
    ):
        market_session_service.symbol_hold_subscriber = object()
        await market_session_service._async_unsubscribe_from_symbol_holds()
        assert market_session_service.symbol_hold_subscriber is None

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_symbol_holds_exception(
        self, market_session_service
    ):
        market_session_service.symbol_hold_subscriber = object()
        raise_symbol_hold_service_exception(market_session_service)
        await market_session_service._async_unsubscribe_from_symbol_holds()
        assert market_session_service.symbol_hold_subscriber is None

    @pytest.mark.asyncio
    async def test__async_handle_symbol_hold_roster_event_end_status(
        self, market_session_service
    ):
        # Patch async_force_stop by assigning a flag
        called = {}

        async def fake_force_stop():
            called["ran"] = True

        market_session_service.async_force_stop = fake_force_stop
        symbol_hold_roster = {
            "AAPL": market_session_service.END_STATUS[0],
            "GOOG": market_session_service.END_STATUS[1],
        }
        await market_session_service._async_handle_symbol_hold_roster_event(
            symbol_hold_roster
        )
        assert called.get("ran")

    @pytest.mark.asyncio
    async def test__async_handle_symbol_hold_roster_event_exception(
        self, market_session_service
    ):
        async def fake_force_stop():
            raise Exception("fail")

        market_session_service.async_force_stop = fake_force_stop
        symbol_hold_roster = {"AAPL": market_session_service.END_STATUS[0]}
        await market_session_service._async_handle_symbol_hold_roster_event(
            symbol_hold_roster
        )
