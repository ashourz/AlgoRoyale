from datetime import datetime
from uuid import UUID

import pytest

from tests.mocks.services.mock_trades_service import MockTradesService


@pytest.fixture
def trades_service():
    service = MockTradesService()
    yield service


@pytest.mark.asyncio
class TestTradesService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, trades_service: MockTradesService):
        print("Setup")
        trades_service.reset()
        yield
        print("Teardown")
        trades_service.reset()

    async def test_fetch_trades_by_order_id_normal(
        self, trades_service: MockTradesService
    ):
        from uuid import uuid4

        order_id = uuid4()
        trades = trades_service.fetch_trades_by_order_id(order_id)
        assert len(trades) == 1
        assert trades[0].order_id == order_id or isinstance(
            trades[0].order_id, type(order_id)
        )

    async def test_fetch_trades_by_order_id_empty(
        self, trades_service: MockTradesService
    ):
        from uuid import uuid4

        trades_service.set_return_empty(True)
        order_id = uuid4()
        trades = trades_service.fetch_trades_by_order_id(order_id)
        assert len(trades) == 0
        trades_service.reset_return_empty()

    async def test_fetch_trades_by_order_id_exception(
        self, trades_service: MockTradesService
    ):
        from uuid import uuid4

        trades_service.set_raise_exception(True)
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_trades_by_order_id(order_id)
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def test_fetch_unsettled_trades_normal(
        self, trades_service: MockTradesService
    ):
        trades = trades_service.fetch_unsettled_trades()
        assert len(trades) == 1
        assert trades[0].settled is False
        assert trades[0].id == UUID("00000000-0000-0000-0000-000000000001")

    async def test_fetch_unsettled_trades_empty(
        self, trades_service: MockTradesService
    ):
        trades_service.set_return_empty(True)
        trades = trades_service.fetch_unsettled_trades()
        assert len(trades) == 0
        trades_service.reset()

    async def test_fetch_unsettled_trades_exception(
        self, trades_service: MockTradesService
    ):
        trades_service.set_raise_exception(True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_unsettled_trades()
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def test_update_settled_trades_normal(
        self, trades_service: MockTradesService
    ):
        trades_service.update_settled_trades()
        assert True  # If no exception is raised, the test passes

    async def test_insert_trade_normal(self, trades_service: MockTradesService):
        trade_id = trades_service.insert_trade(
            symbol="AAPL",
            action="buy",
            settled=False,
            settlement_date="2023-10-01",
            price=100.0,
            quantity=10,
            executed_at=datetime.now(),
        )
        assert trade_id == "00000000-0000-0000-0000-000000000003"

    async def test_insert_trade_exception(self, trades_service: MockTradesService):
        trades_service.set_raise_exception(True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.insert_trade(
                symbol="AAPL",
                action="buy",
                settled=False,
                settlement_date="2023-10-01",
                price=100.0,
                quantity=10,
                executed_at=datetime.now(),
            )
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def test_fetch_trades_by_date_range_normal(
        self, trades_service: MockTradesService
    ):
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        trades = trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 1

    async def test_fetch_trades_by_date_range_empty(
        self, trades_service: MockTradesService
    ):
        from datetime import datetime, timedelta

        trades_service.set_return_empty(True)
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        trades = trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 0
        trades_service.reset_return_empty()

    async def test_fetch_trades_by_date_range_exception(
        self, trades_service: MockTradesService
    ):
        from datetime import datetime, timedelta

        trades_service.set_raise_exception(True)
        start_date = datetime.now() - timedelta(days=2)
        end_date = datetime.now()
        with pytest.raises(ValueError) as excinfo:
            trades_service.fetch_trades_by_date_range(start_date, end_date)
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def test_delete_trade_normal(self, trades_service: MockTradesService):
        trade_id = trades_service.insert_trade(
            symbol="AAPL",
            action="buy",
            settled=False,
            settlement_date="2023-10-01",
            price=100.0,
            quantity=10,
            executed_at=datetime.now(),
        )
        deleted_count = trades_service.delete_trade(trade_id)
        assert deleted_count == 1

    async def test_delete_trade_exception(self, trades_service: MockTradesService):
        from uuid import uuid4

        trades_service.set_raise_exception(True)
        trade_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            trades_service.delete_trade(trade_id)
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def test_delete_all_trades_normal(self, trades_service: MockTradesService):
        deleted_count = trades_service.delete_all_trades()
        assert deleted_count == 1

    async def test_delete_all_trades_exception(self, trades_service: MockTradesService):
        trades_service.set_raise_exception(True)
        with pytest.raises(ValueError) as excinfo:
            trades_service.delete_all_trades()
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()

    async def reconcole_trades_normal(self, trades_service: MockTradesService):
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        trades_service.reconcile_trades(start_date=start_date, end_date=end_date)
        assert True  # If no exception is raised, the test passes

    async def reconcole_trades_exception(self, trades_service: MockTradesService):
        from datetime import datetime, timedelta

        trades_service.set_raise_exception(True)
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        with pytest.raises(ValueError) as excinfo:
            trades_service.reconcile_trades(start_date=start_date, end_date=end_date)
        assert "Database error" in str(excinfo.value)
        trades_service.reset_raise_exception()
