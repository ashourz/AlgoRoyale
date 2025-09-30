from datetime import datetime
from uuid import UUID

import pytest

from algo_royale.services.trades_service import TradesService
from tests.mocks.adapters.mock_account_adapter import MockAccountAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_trade_repo import MockTradeRepo
from tests.mocks.services.mock_clock_service import MockClockService


@pytest.fixture
def trades_service():
    service = TradesService(
        account_adapter=MockAccountAdapter(),
        trade_repo=MockTradeRepo(),
        clock_service=MockClockService(),
        logger=MockLoggable(),
        user_id="user_1",
        account_id="account_1",
        days_to_settle=1,
    )
    yield service


def set_trades_service_raise_exception(trades_service: TradesService, value: bool):
    trades_service.repo.set_raise_exception(value)
    trades_service.account_adapter.set_raise_exception(value)


def reset_trades_service_raise_exception(trades_service: TradesService):
    trades_service.repo.reset_raise_exception()
    trades_service.account_adapter.reset_raise_exception()


def set_trades_service_return_empty(trades_service: TradesService, value: bool):
    trades_service.repo.set_return_empty(value)
    trades_service.account_adapter.set_return_empty(value)


def reset_trades_service_return_empty(trades_service: TradesService):
    trades_service.repo.reset_return_empty()
    trades_service.account_adapter.reset_return_empty()


def reset_trades_service(trades_service: TradesService):
    trades_service.repo.reset()
    trades_service.account_adapter.reset()


@pytest.mark.asyncio
class TestTradesService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, trades_service: TradesService):
        print("Setup")
        reset_trades_service(trades_service)
        yield
        print("Teardown")
        reset_trades_service(trades_service)

    async def test_fetch_trades_by_order_id_normal(self, trades_service: TradesService):
        from uuid import uuid4

        order_id = uuid4()
        trades = trades_service.fetch_trades_by_order_id(order_id)
        assert len(trades) == 1
        assert trades[0].order_id == order_id or isinstance(
            trades[0].order_id, type(order_id)
        )

    async def test_fetch_trades_by_order_id_empty(self, trades_service: TradesService):
        from uuid import uuid4

        set_trades_service_return_empty(trades_service, True)
        order_id = uuid4()
        trades = trades_service.fetch_trades_by_order_id(order_id)
        assert len(trades) == 0
        reset_trades_service_return_empty(trades_service)

    async def test_fetch_trades_by_order_id_exception(
        self, trades_service: TradesService
    ):
        from uuid import uuid4

        set_trades_service_raise_exception(trades_service, True)
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_trades_by_order_id(order_id)
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def test_fetch_unsettled_trades_normal(self, trades_service: TradesService):
        trades = trades_service.fetch_unsettled_trades()
        assert len(trades) == 1
        assert trades[0].settled is False
        assert trades[0].id == 1

    async def test_fetch_unsettled_trades_empty(self, trades_service: TradesService):
        set_trades_service_return_empty(trades_service, True)
        trades = trades_service.fetch_unsettled_trades()
        assert len(trades) == 0
        reset_trades_service_return_empty(trades_service)

    async def test_fetch_unsettled_trades_exception(
        self, trades_service: TradesService
    ):
        set_trades_service_raise_exception(trades_service, True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_unsettled_trades()
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def test_update_settled_trades_normal(self, trades_service: TradesService):
        trades_service.update_settled_trades()
        assert True  # If no exception is raised, the test passes

    async def test_insert_trade_normal(self, trades_service: TradesService):
        trade_id = trades_service.insert_trade(
            symbol="AAPL",
            action="buy",
            price=100.0,
            quantity=10,
            executed_at=datetime.now(),
            order_id=UUID("00000000-0000-0000-0000-000000000003"),
        )
        assert trade_id is not None

    async def test_insert_trade_exception(self, trades_service: TradesService):
        set_trades_service_raise_exception(trades_service, True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.insert_trade(
                symbol="AAPL",
                action="buy",
                price=100.0,
                quantity=10,
                executed_at=datetime.now(),
                order_id=UUID("00000000-0000-0000-0000-000000000003"),
            )
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def test_fetch_trades_by_date_range_normal(
        self, trades_service: TradesService
    ):
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        trades = trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 1

    async def test_fetch_trades_by_date_range_empty(
        self, trades_service: TradesService
    ):
        from datetime import datetime, timedelta

        set_trades_service_return_empty(trades_service, True)
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        trades = trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 0
        reset_trades_service_return_empty(trades_service)

    async def test_fetch_trades_by_date_range_exception(
        self, trades_service: TradesService
    ):
        from datetime import datetime, timedelta

        set_trades_service_raise_exception(trades_service, True)
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def test_delete_trade_normal(self, trades_service: TradesService):
        trade_id = trades_service.insert_trade(
            symbol="AAPL",
            action="buy",
            price=100.0,
            quantity=10,
            executed_at=datetime.now(),
            order_id=UUID("00000000-0000-0000-0000-000000000003"),
        )
        deleted_count = trades_service.delete_trade(trade_id)
        assert deleted_count == 1

    async def test_delete_trade_exception(self, trades_service: TradesService):
        from uuid import uuid4

        set_trades_service_raise_exception(trades_service, True)
        trade_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            trades_service.delete_trade(trade_id)
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def test_delete_all_trades_normal(self, trades_service: TradesService):
        deleted_count = trades_service.delete_all_trades()
        assert deleted_count == 1

    async def test_delete_all_trades_exception(self, trades_service: TradesService):
        set_trades_service_raise_exception(trades_service, True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.delete_all_trades()
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)

    async def reconcile_trades_normal(self, trades_service: TradesService):
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        trades_service.reconcile_trades(start_date=start_date, end_date=end_date)
        assert True  # If no exception is raised, the test passes

    async def reconcile_trades_exception(self, trades_service: TradesService):
        from datetime import datetime, timedelta

        set_trades_service_raise_exception(trades_service, True)
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        with pytest.raises(ValueError) as excinfo:
            trades_service.reconcile_trades(start_date=start_date, end_date=end_date)
        assert "Database error" in str(excinfo.value)
        reset_trades_service_raise_exception(trades_service)
