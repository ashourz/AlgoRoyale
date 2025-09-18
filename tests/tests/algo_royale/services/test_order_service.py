import pytest

from algo_royale.application.orders.equity_order_enums import (
    EquityOrderClass,
    EquityOrderSide,
    EquityTimeInForce,
)
from algo_royale.application.orders.equity_order_types import EquityMarketNotionalOrder
from algo_royale.services.orders_service import OrderService
from tests.mocks.adapters.mock_orders_adapter import MockOrdersAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_order_repo import MockOrderRepo
from tests.mocks.repo.mock_trade_repo import MockTradeRepo


@pytest.fixture
def order_service():
    service = OrderService(
        orders_adapter=MockOrdersAdapter(),
        order_repo=MockOrderRepo(),
        trade_repo=MockTradeRepo(),
        logger=MockLoggable(),
        user_id="user_1",
        account_id="account_1",
    )
    yield service


def set_order_service_return_empty(order_service: OrderService, value: bool):
    order_service.orders_adapter.set_return_empty(value)
    order_service.order_repo.set_return_empty(value)
    order_service.trade_repo.set_return_empty(value)


def reset_order_service_return_empty(order_service: OrderService):
    order_service.orders_adapter.reset_return_empty()
    order_service.order_repo.reset_return_empty()
    order_service.trade_repo.reset_return_empty()


def set_order_service_raise_exception(order_service: OrderService, value: bool):
    order_service.orders_adapter.set_raise_exception(value)
    order_service.order_repo.set_raise_exception(value)
    order_service.trade_repo.set_raise_exception(value)


def reset_order_service_raise_exception(order_service: OrderService):
    order_service.orders_adapter.reset_raise_exception()
    order_service.order_repo.reset_raise_exception()
    order_service.trade_repo.reset_raise_exception()


def reset(order_service: OrderService):
    reset_order_service_return_empty(order_service)
    reset_order_service_raise_exception(order_service)


@pytest.mark.asyncio
class TestOrderService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_service: OrderService):
        print("Setup")
        reset
        yield
        print("Teardown")
        reset(order_service)

    async def test_fetch_orders_by_symbol_and_status(self, order_service: OrderService):
        orders = order_service.fetch_orders_by_symbol_and_status("AAPL", "open")
        assert isinstance(orders, list)

    async def test_fetch_orders_by_symbol_and_status_empty(
        self, order_service: OrderService
    ):
        set_order_service_return_empty(order_service, True)
        orders = order_service.fetch_orders_by_symbol_and_status(
            symbol="AAPL", status_list=["open"]
        )
        assert orders == [] or orders is None

    async def test_fetch_orders_by_symbol_and_status_exception(
        self, order_service: OrderService
    ):
        set_order_service_raise_exception(order_service, True)
        result = order_service.fetch_orders_by_symbol_and_status(
            symbol="AAPL", status_list=["open"]
        )
        assert result == []

    async def test_update_order(self, order_service: OrderService):
        order_id = order_service.order_repo.dao.test_order.id
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == 1

    async def test_update_order_exception(self, order_service: OrderService):
        order_id = order_service.order_repo.dao.test_order.id
        set_order_service_raise_exception(order_service, True)
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == -1

    async def test_update_order_empty(self, order_service: OrderService):
        order_id = order_service.order_repo.dao.test_order.id
        set_order_service_return_empty(order_service, True)
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == 0

    async def test_fetch_order_by_id(self, order_service: OrderService):
        order_id = order_service.order_repo.dao.test_order.id
        order = order_service.fetch_order_by_id(order_id)
        assert order is not None
        assert order.id == order_id

    async def test_fetch_order_by_id_exception(self, order_service: OrderService):
        order_id = order_service.order_repo.dao.test_order.id
        set_order_service_raise_exception(order_service, True)
        order = order_service.fetch_order_by_id(order_id)
        assert order is None

    async def test_submit_order(self, order_service: OrderService):
        order = EquityMarketNotionalOrder(
            symbol="AAPL",
            notional=100.0,
            side=EquityOrderSide.BUY,
            time_in_force=EquityTimeInForce.DAY,
            order_class=EquityOrderClass.SIMPLE,
            client_order_id="test_order_123",
        )
        order_id = await order_service.submit_order(order)
        assert order_id is not None

    async def test_submit_order_exception(self, order_service: OrderService):
        order = EquityMarketNotionalOrder(
            symbol="AAPL",
            notional=100.0,
            side=EquityOrderSide.BUY,
            time_in_force=EquityTimeInForce.DAY,
            order_class=EquityOrderClass.SIMPLE,
            client_order_id="test_order_123",
        )
        set_order_service_raise_exception(order_service, True)
        order_id = await order_service.submit_order(order)
        assert order_id is None

    async def test_submit_order_empty(self, order_service: OrderService):
        order = EquityMarketNotionalOrder(
            symbol="AAPL",
            notional=100.0,
            side=EquityOrderSide.BUY,
            time_in_force=EquityTimeInForce.DAY,
            order_class=EquityOrderClass.SIMPLE,
        )
        set_order_service_return_empty(order_service, True)
        order_id = await order_service.submit_order(order)
        assert order_id is None

    async def test_update_settled_orders(self, order_service: OrderService):
        order_service.update_settled_orders()
        assert True  # If no exceptions, the test passes

    async def test_update_settled_orders_exception(self, order_service: OrderService):
        set_order_service_raise_exception(order_service, True)
        order_service.update_settled_orders()
        assert True  # If no exceptions, the test passes
