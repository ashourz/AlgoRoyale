from uuid import uuid4

import pytest

from algo_royale.repo.order_repo import DBOrderStatus, OrderAction, OrderType
from tests.mocks.repo.mock_order_repo import MockOrderRepo


@pytest.fixture
def order_repo():
    adapter = MockOrderRepo()
    yield adapter


@pytest.mark.asyncio
class TestOrderRepo:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_repo: MockOrderRepo):
        print("Setup")
        order_repo.reset_return_empty()
        order_repo.reset_raise_exception()
        order_repo.reset_dao()
        yield
        print("Teardown")
        order_repo.reset_return_empty()
        order_repo.reset_raise_exception()
        order_repo.reset_dao()

    async def test_fetch_order_by_id_normal(self, order_repo):
        order_id = uuid4()
        orders = order_repo.fetch_order_by_id(order_id, "user_1", "account_1")
        assert len(orders) == 1
        assert orders[0].id is not None

    async def test_fetch_order_by_id_empty(self, order_repo):
        order_repo._return_empty = True
        order_id = uuid4()
        orders = order_repo.fetch_order_by_id(order_id, "user_1", "account_1")
        assert len(orders) == 0

    async def test_fetch_order_by_id_exception(self, order_repo):
        order_repo._raise_exception = True
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            order_repo.fetch_order_by_id(order_id, "user_1", "account_1")
        assert "Database error" in str(excinfo.value)

    async def test_insert_order_normal(self, order_repo):
        symbol = "AAPL"
        notional = 1000.0
        order_id = order_repo.insert_order(
            symbol=symbol,
            order_type=OrderType.MARKET,
            status=DBOrderStatus.NEW,
            action=OrderAction.BUY,
            notional=notional,
            quantity=10,
            price=100.0,
        )
        assert order_id == f"mock_order_{symbol}_{notional}"

    async def test_insert_order_exception(self, order_repo):
        order_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            order_repo.insert_order(
                symbol="AAPL",
                order_type=OrderType.MARKET,
                status=DBOrderStatus.NEW,
                action=OrderAction.BUY,
                notional=1000.0,
                quantity=10,
                price=100.0,
            )
        assert "Database error" in str(excinfo.value)

    async def test_delete_order_normal(self, order_repo):
        order_id = uuid4()
        deleted = order_repo.delete_order(order_id)
        assert deleted == 1

    async def test_delete_order_exception(self, order_repo):
        order_repo._raise_exception = True
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            order_repo.delete_order(order_id)
        assert "Database error" in str(excinfo.value)

    async def test_delete_all_orders_normal(self, order_repo):
        deleted = order_repo.delete_all_orders()
        assert deleted == 1

    async def test_delete_all_orders_exception(self, order_repo):
        order_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            order_repo.delete_all_orders()
        assert "Database error" in str(excinfo.value)
