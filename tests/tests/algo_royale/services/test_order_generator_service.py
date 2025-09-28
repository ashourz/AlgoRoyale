import pytest

from algo_royale.services.order_generator_service import OrderGeneratorService
from tests.mocks.application.mock_order_generator import MockOrderGenerator
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_symbol_hold_service import MockSymbolHoldService


@pytest.fixture
def market_session_service():
    service = OrderGeneratorService(
        order_generator=MockOrderGenerator(),
        symbol_hold_service=MockSymbolHoldService(),
        logger=MockLoggable(),
    )
    yield service


def set_return_empty_symbol_hold_service(service: OrderGeneratorService):
    service.symbol_hold_service.set_return_empty(True)


def set_raise_exception_symbol_hold_service(service: OrderGeneratorService):
    service.symbol_hold_service.set_raise_exception(True)


def set_return_empty_order_generator(service: OrderGeneratorService):
    service.order_generator.set_return_empty(True)


def reset_services(service: OrderGeneratorService):
    service.symbol_hold_service.reset()
    service.order_generator.reset()


@pytest.mark.asyncio
class TestOrderGeneratorService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, market_session_service: OrderGeneratorService):
        print("Setup")
        yield
        print("Teardown")
        reset_services(market_session_service)

    @pytest.mark.asyncio
    async def test_subscribe_to_symbol_orders_success(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        assert isinstance(result, dict)
        assert all(isinstance(sub, object) for sub in result.values())

    @pytest.mark.asyncio
    async def test_subscribe_to_symbol_orders_empty(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        set_return_empty_order_generator(market_session_service)
        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_subscribe_to_symbol_orders_exception(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        set_raise_exception_symbol_hold_service(market_session_service)
        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        assert isinstance(result, dict)
        assert all(isinstance(sub, object) for sub in result.values())

    @pytest.mark.asyncio
    async def test_unsubscribe_from_symbol_orders_success(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        await market_session_service.unsubscribe_from_symbol_orders(result)
        # Should not raise

    @pytest.mark.asyncio
    async def test_unsubscribe_from_symbol_orders_exception(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        set_raise_exception_symbol_hold_service(market_session_service)
        await market_session_service.unsubscribe_from_symbol_orders(result)
        # Should not raise

    @pytest.mark.asyncio
    async def test__await_subscribe_to_symbol_hold_success(
        self, market_session_service: OrderGeneratorService
    ):
        await market_session_service._await_subscribe_to_symbol_hold()
        # Should not raise

    @pytest.mark.asyncio
    async def test__await_subscribe_to_symbol_hold_exception(
        self, market_session_service: OrderGeneratorService
    ):
        set_raise_exception_symbol_hold_service(market_session_service)
        await market_session_service._await_subscribe_to_symbol_hold()
        # Should not raise

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_symbol_hold_success(
        self, market_session_service: OrderGeneratorService
    ):
        await market_session_service._await_subscribe_to_symbol_hold()
        await market_session_service._async_unsubscribe_from_symbol_hold()
        # Should not raise

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_symbol_hold_exception(
        self, market_session_service: OrderGeneratorService
    ):
        await market_session_service._await_subscribe_to_symbol_hold()
        set_raise_exception_symbol_hold_service(market_session_service)
        await market_session_service._async_unsubscribe_from_symbol_hold()
        # Should not raise

    @pytest.mark.asyncio
    async def test__async_subscribe_to_orders_success(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service._async_subscribe_to_orders(
            symbols, callback
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test__async_subscribe_to_orders_empty(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        set_return_empty_order_generator(market_session_service)
        result = await market_session_service._async_subscribe_to_orders(
            symbols, callback
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test__async_subscribe_to_orders_exception(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        set_raise_exception_symbol_hold_service(market_session_service)
        result = await market_session_service._async_subscribe_to_orders(
            symbols, callback
        )
        assert isinstance(result, dict)
        assert all(isinstance(sub, object) for sub in result.values())

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_orders_success(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        await market_session_service._async_unsubscribe_from_orders(result)
        # Should not raise

    @pytest.mark.asyncio
    async def test__async_unsubscribe_from_orders_exception(
        self, market_session_service: OrderGeneratorService
    ):
        symbols = ["AAPL", "GOOG"]

        def callback(x):
            pass

        result = await market_session_service.subscribe_to_symbol_orders(
            symbols, callback
        )
        set_raise_exception_symbol_hold_service(market_session_service)
        await market_session_service._async_unsubscribe_from_orders(result)
        # Should not raise
