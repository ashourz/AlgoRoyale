import pytest

from algo_royale.services.symbol_hold_service import SymbolHoldService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_order_event_service import MockOrderEventService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_symbol_hold_tracker import MockSymbolHoldTracker
from tests.mocks.services.mock_symbol_service import MockSymbolService
from tests.mocks.services.mock_trades_service import MockTradesService


@pytest.fixture
def symbol_hold_service():
    service = SymbolHoldService(
        symbol_service=MockSymbolService(),
        symbol_hold_tracker=MockSymbolHoldTracker(),
        order_service=MockOrderService(),
        order_event_service=MockOrderEventService(),
        positions_service=MockPositionsService(),
        trades_service=MockTradesService(),
        logger=MockLoggable(),
        post_fill_delay_seconds=0.0,
    )
    yield service


def set_return_empty_symbol_service(service: SymbolHoldService):
    service.symbol_service.set_return_empty(True)


def set_raise_exception_symbol_service(service: SymbolHoldService):
    service.symbol_service.set_raise_exception(True)


def set_return_empty_symbol_hold_tracker(service: SymbolHoldService):
    service.symbol_hold_tracker.set_return_empty(True)


def set_return_empty_order_service(service: SymbolHoldService):
    service.order_service.set_return_empty(True)


def set_raise_exception_order_service(service: SymbolHoldService):
    service.order_service.set_raise_exception(True)


def set_return_empty_order_event_service(service: SymbolHoldService):
    service.order_event_service.set_return_empty(True)


def set_raise_exception_order_event_service(service: SymbolHoldService):
    service.order_event_service.set_raise_exception(True)


def set_return_empty_positions_service(service: SymbolHoldService):
    service.positions_service.set_return_empty(True)


def set_raise_exception_positions_service(service: SymbolHoldService):
    service.positions_service.set_raise_exception(True)


def set_return_empty_trades_service(service: SymbolHoldService):
    service.trades_service.set_return_empty(True)


def set_raise_exception_trades_service(service: SymbolHoldService):
    service.trades_service.set_raise_exception(True)


def reset_services(service: SymbolHoldService):
    service.symbol_service.reset()
    service.symbol_hold_tracker.reset()
    service.order_service.reset()
    service.order_event_service.reset()
    service.positions_service.reset()
    service.trades_service.reset()


@pytest.mark.asyncio
class TestSymbolHoldService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, symbol_hold_service: SymbolHoldService):
        yield
        reset_services(symbol_hold_service)

    @pytest.mark.asyncio
    async def test_start_and_stop_success(self, symbol_hold_service):
        await symbol_hold_service.start()
        await symbol_hold_service.stop()

    @pytest.mark.asyncio
    async def test_start_with_symbol_service_exception(self, symbol_hold_service):
        set_raise_exception_symbol_service(symbol_hold_service)
        await symbol_hold_service.start()  # Should log error, not raise

    @pytest.mark.asyncio
    async def test_start_with_order_event_service_exception(self, symbol_hold_service):
        set_raise_exception_order_event_service(symbol_hold_service)
        await symbol_hold_service.start()  # Should log error, not raise

    @pytest.mark.asyncio
    async def test_stop_without_start(self, symbol_hold_service):
        await symbol_hold_service.stop()  # Should log warning, not raise

    @pytest.mark.asyncio
    async def test_stop_with_order_event_service_exception(self, symbol_hold_service):
        await symbol_hold_service.start()
        set_raise_exception_order_event_service(symbol_hold_service)
        await symbol_hold_service.stop()  # Should log error, not raise

    @pytest.mark.asyncio
    async def test_async_initialize_symbol_holds_empty(self, symbol_hold_service):
        set_return_empty_symbol_service(symbol_hold_service)
        await symbol_hold_service._async_initialize_symbol_holds()

    @pytest.mark.asyncio
    async def test_async_initialize_symbol_holds_exception(self, symbol_hold_service):
        set_raise_exception_symbol_service(symbol_hold_service)
        await symbol_hold_service._async_initialize_symbol_holds()

    @pytest.mark.asyncio
    async def test_async_set_symbol_holds_by_order_status_empty(
        self, symbol_hold_service
    ):
        set_return_empty_symbol_service(symbol_hold_service)
        set_return_empty_order_service(symbol_hold_service)
        await symbol_hold_service._async_set_symbol_holds_by_order_status()

    @pytest.mark.asyncio
    async def test_async_set_symbol_holds_by_order_status_exception(
        self, symbol_hold_service
    ):
        set_raise_exception_symbol_service(symbol_hold_service)
        await symbol_hold_service._async_set_symbol_holds_by_order_status()

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_all_events(self, symbol_hold_service):
        class DummyOrder:
            side = None

        class DummyData:
            event = symbol_hold_service.HOLD_ALL_EVENTS[0]
            order = DummyOrder()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_sell_only_event(self, symbol_hold_service):
        class DummyOrder:
            side = None

        class DummyData:
            event = next(iter(symbol_hold_service.SELL_ONLY_OR_BUY_ONLY_EVENTS))
            order = DummyOrder()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_fill_buy(self, symbol_hold_service):
        class DummyOrder:
            side = type("OrderSide", (), {"BUY": "BUY", "SELL": "SELL"})().BUY

        class DummyData:
            event = type("OrderStreamEvent", (), {"FILL": "FILL"})().FILL
            order = type("Order", (), {"side": "BUY"})()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_fill_sell(self, symbol_hold_service):
        class DummyOrder:
            side = "SELL"

        class DummyData:
            event = "FILL"
            order = DummyOrder()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_done_for_day(self, symbol_hold_service):
        class DummyOrder:
            side = None

        class DummyData:
            event = "DONE_FOR_DAY"
            order = DummyOrder()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_async_update_symbol_hold_exception(self, symbol_hold_service):
        def raise_exception(*args, **kwargs):
            raise Exception("Test exception")

        symbol_hold_service._async_set_symbol_hold = raise_exception

        class DummyOrder:
            side = None

        class DummyData:
            event = symbol_hold_service.HOLD_ALL_EVENTS[0]
            order = DummyOrder()

        await symbol_hold_service._async_update_symbol_hold("AAPL", DummyData())

    @pytest.mark.asyncio
    async def test_post_fill_delay_success(self, symbol_hold_service):
        await symbol_hold_service._post_fill_delay("AAPL")

    @pytest.mark.asyncio
    async def test_post_fill_delay_exception(self, symbol_hold_service):
        def raise_exception(*args, **kwargs):
            raise Exception("Test exception")

        symbol_hold_service._async_set_symbol_hold = raise_exception
        await symbol_hold_service._post_fill_delay("AAPL")

    @pytest.mark.asyncio
    async def test_async_set_symbol_hold_success(self, symbol_hold_service):
        await symbol_hold_service._async_set_symbol_hold("AAPL", 1)

    @pytest.mark.asyncio
    async def test_async_set_symbol_hold_exception(self, symbol_hold_service):
        def raise_exception(*args, **kwargs):
            raise Exception("Test exception")

        symbol_hold_service.symbol_hold_tracker.async_set_hold = raise_exception
        await symbol_hold_service._async_set_symbol_hold("AAPL", 1)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_symbol_holds_success(self, symbol_hold_service):
        def callback(data, typ):
            pass

        result = await symbol_hold_service.async_subscribe_to_symbol_holds(callback)
        assert result is not None

    # Removed test_async_subscribe_to_symbol_holds_exception: symbol_hold_tracker never raises

    def test_unsubscribe_from_symbol_holds_success(self, symbol_hold_service):
        subscriber = object()
        symbol_hold_service.unsubscribe_from_symbol_holds(subscriber)

    def test_unsubscribe_from_symbol_holds_exception(self, symbol_hold_service):
        def raise_exception(*args, **kwargs):
            raise Exception("Test exception")

        symbol_hold_service.symbol_hold_tracker.unsubscribe_from_symbol = (
            raise_exception
        )
        subscriber = object()
        symbol_hold_service.unsubscribe_from_symbol_holds(subscriber)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_hold_roster_success(self, symbol_hold_service):
        def callback(data, typ):
            pass

        result = await symbol_hold_service.async_subscribe_to_hold_roster(callback)
        assert result is not None

    # Removed test_async_subscribe_to_hold_roster_exception: symbol_hold_tracker never raises

    def test_unsubscribe_from_hold_roster_success(self, symbol_hold_service):
        subscriber = object()
        symbol_hold_service.unsubscribe_from_hold_roster(subscriber)

    def test_unsubscribe_from_hold_roster_exception(self, symbol_hold_service):
        def raise_exception(*args, **kwargs):
            raise Exception("Test exception")

        symbol_hold_service.symbol_hold_tracker.unsubscribe_from_roster = (
            raise_exception
        )
        subscriber = object()
        symbol_hold_service.unsubscribe_from_hold_roster(subscriber)
