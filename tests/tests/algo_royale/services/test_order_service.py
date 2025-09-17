import pytest

from algo_royale.application.orders.equity_order_enums import (
    EquityOrderClass,
    EquityOrderSide,
    EquityTimeInForce,
)
from algo_royale.application.orders.equity_order_types import EquityMarketNotionalOrder
from tests.mocks.services.mock_order_service import MockOrderService


@pytest.fixture
def order_service():
    service = MockOrderService()
    yield service


@pytest.mark.asyncio
class TestOrderService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_service: MockOrderService):
        print("Setup")
        order_service.reset()
        yield
        print("Teardown")
        order_service.reset()

    async def test_fetch_orders_by_symbol_and_status(
        self, order_service: MockOrderService
    ):
        orders = order_service.fetch_orders_by_symbol_and_status("AAPL", "open")
        assert isinstance(orders, list)

    async def test_fetch_orders_by_symbol_and_status_empty(
        self, order_service: MockOrderService
    ):
        order_service.set_return_empty(True)
        orders = order_service.fetch_orders_by_symbol_and_status(
            symbol="AAPL", status_list=["open"]
        )
        assert orders == [] or orders is None

    async def test_fetch_orders_by_symbol_and_status_exception(
        self, order_service: MockOrderService
    ):
        order_service.set_raise_exception(True)
        result = order_service.fetch_orders_by_symbol_and_status(
            symbol="AAPL", status_list=["open"]
        )
        assert result == []

    async def test_update_order(self, order_service: MockOrderService):
        order_id = order_service.order_repo.dao.test_order.id
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == 1

    async def test_update_order_exception(self, order_service: MockOrderService):
        order_id = order_service.order_repo.dao.test_order.id
        order_service.set_raise_exception(True)
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == -1

    async def test_update_order_empty(self, order_service: MockOrderService):
        order_id = order_service.order_repo.dao.test_order.id
        order_service.set_return_empty(True)
        update_count = order_service.update_order(
            order_id=order_id, status="filled", quantity=5, price=150.0
        )
        assert update_count == 0

    async def test_fetch_order_by_id(self, order_service: MockOrderService):
        order_id = order_service.order_repo.dao.test_order.id
        order = order_service.fetch_order_by_id(order_id)
        assert order is not None
        assert order.id == order_id

    async def test_fetch_order_by_id_exception(self, order_service: MockOrderService):
        order_id = order_service.order_repo.dao.test_order.id
        order_service.set_raise_exception(True)
        order = order_service.fetch_order_by_id(order_id)
        assert order is None

    async def test_submit_order(self, order_service: MockOrderService):
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

    async def test_submit_order_exception(self, order_service: MockOrderService):
        order = EquityMarketNotionalOrder(
            symbol="AAPL",
            notional=100.0,
            side=EquityOrderSide.BUY,
            time_in_force=EquityTimeInForce.DAY,
            order_class=EquityOrderClass.SIMPLE,
            client_order_id="test_order_123",
        )
        order_service.set_raise_exception(True)
        order_id = await order_service.submit_order(order)
        assert order_id is None

    async def test_submit_order_empty(self, order_service: MockOrderService):
        order = EquityMarketNotionalOrder(
            symbol="AAPL",
            notional=100.0,
            side=EquityOrderSide.BUY,
            time_in_force=EquityTimeInForce.DAY,
            order_class=EquityOrderClass.SIMPLE,
        )
        order_service.set_return_empty(True)
        order_id = await order_service.submit_order(order)
        assert order_id is None

    async def test_update_settled_orders(self, order_service: MockOrderService):
        order_service.update_settled_orders()
        assert True  # If no exceptions, the test passes

    async def test_update_settled_orders_exception(
        self, order_service: MockOrderService
    ):
        order_service.set_raise_exception(True)
        order_service.update_settled_orders()
        assert True  # If no exceptions, the test passes
