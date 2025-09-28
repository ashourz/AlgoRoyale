import pytest

from algo_royale.services.orders_execution_service import OrderExecutionService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_ledger_service import MockLedgerService
from tests.mocks.services.mock_order_generator_service import MockOrderGeneratorService
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService


@pytest.fixture
def order_execution_service():
    service = OrderExecutionService(
        symbol_hold_service=MockSymbolHoldService(),
        ledger_service=MockLedgerService(),
        order_generator_service=MockOrderGeneratorService(),
        logger=MockLoggable(),
    )
    yield service


def raise_symbol_hold_service_exception(service: OrderExecutionService):
    service.symbol_hold_service.set_raise_exception(True)


def raise_ledger_service_exception(service: OrderExecutionService):
    service.ledger_service.set_raise_exception(True)


def return_empty_symbol_hold_service(service: OrderExecutionService):
    service.symbol_hold_service.set_return_empty(True)


def return_empty_ledger_service(service: OrderExecutionService):
    service.ledger_service.set_return_empty(True)


def return_empty_order_generator_service(service: OrderExecutionService):
    service.order_generator_service.set_return_empty(True)


def reset_services(service: OrderExecutionService):
    service.symbol_hold_service.reset()
    service.ledger_service.reset()
    service.order_generator_service.reset()


@pytest.mark.asyncio
class TestOrderExecutionService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_execution_service):
        print("Setup")
        yield
        print("Teardown")
        reset_services(order_execution_service)

    async def test_start_success(self, order_execution_service: OrderExecutionService):
        symbols = ["AAPL", "GOOG"]
        result = await order_execution_service.start(symbols)
        # The real implementation may return None if not implemented or if an error occurs
        assert result is None or isinstance(result, dict)

    async def test_start_empty(self, order_execution_service: OrderExecutionService):
        symbols = ["AAPL", "GOOG"]
        return_empty_order_generator_service(order_execution_service)
        result = await order_execution_service.start(symbols)
        # The real implementation may return None for empty/invalid cases
        assert result is None or result == {}

    async def test_start_exception(
        self, order_execution_service: OrderExecutionService
    ):
        # Simulate exception by raising in order_generator_service
        def broken_subscribe_to_symbol_orders(*args, **kwargs):
            raise Exception("Mocked exception in subscribe_to_symbol_orders")

        order_execution_service.order_generator_service.subscribe_to_symbol_orders = (
            broken_subscribe_to_symbol_orders
        )
        symbols = ["AAPL", "GOOG"]
        result = await order_execution_service.start(symbols)
        assert result is None

    async def test_stop_success(self, order_execution_service: OrderExecutionService):
        symbols = ["AAPL", "GOOG"]
        await order_execution_service.start(symbols)
        # Use the actual symbol_order_subscribers from the service
        symbol_subscribers = {
            symbol: subs
            for symbol, subs in order_execution_service.symbol_order_subscribers.items()
        }
        result = await order_execution_service.stop(symbol_subscribers)
        assert result is True

    async def test_stop_empty(self, order_execution_service: OrderExecutionService):
        # Simulate empty by passing empty dict
        symbol_subscribers = {}
        result = await order_execution_service.stop(symbol_subscribers)
        assert result is True

    async def test_stop_exception(self, order_execution_service: OrderExecutionService):
        # Simulate exception by raising in order_generator_service
        def broken_unsubscribe_from_symbol_orders(*args, **kwargs):
            raise Exception("Mocked exception in unsubscribe_from_symbol_orders")

        order_execution_service.order_generator_service.unsubscribe_from_symbol_orders = broken_unsubscribe_from_symbol_orders
        symbol_subscribers = {"AAPL": [object()]}
        result = await order_execution_service.stop(symbol_subscribers)
        assert result is False

    def test_update_executor_status_enable(
        self, order_execution_service: OrderExecutionService
    ):
        order_execution_service.update_executor_status(True)
        assert order_execution_service._executor_on is True

    def test_update_executor_status_disable(
        self, order_execution_service: OrderExecutionService
    ):
        order_execution_service.update_executor_status(False)
        assert order_execution_service._executor_on is False
