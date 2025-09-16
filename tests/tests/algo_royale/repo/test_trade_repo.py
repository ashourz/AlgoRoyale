import pytest

from algo_royale.repo.trade_repo import TradeRepo
from tests.mocks.repo.mock_trade_repo import MockTradeRepo


@pytest.fixture
def trade_repo():
    adapter = MockTradeRepo()
    yield adapter


@pytest.mark.asyncio
class TestTradeRepo:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, trade_repo: MockTradeRepo):
        # Code to run before each test
        print("Setup")
        trade_repo.reset_return_empty()
        trade_repo.reset_raise_exception()
        trade_repo.reset_dao()
        yield
        # Code to run after each test
        print("Teardown")
        trade_repo.reset_return_empty()
        trade_repo.reset_raise_exception()
        trade_repo.reset_dao()

    async def test_fetch_unsettled_trades_normal(self, trade_repo):
        trades = trade_repo.fetch_unsettled_trades()
        assert len(trades) == 1
        assert trades[0].settled is False
        assert trades[0].id == 1

    async def test_fetch_unsettled_trades_empty(self, trade_repo):
        trade_repo._return_empty = True
        trades = trade_repo.fetch_unsettled_trades()
        assert len(trades) == 0

    async def test_fetch_unsettled_trades_exception(self, trade_repo):
        trade_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            trade_repo.fetch_unsettled_trades()
        assert "Database error" in str(excinfo.value)

    async def test_insert_trade_normal(self, trade_repo):
        from datetime import datetime, timedelta
        from decimal import Decimal
        from uuid import uuid4

        order_id = uuid4()
        trade_id = trade_repo.insert_trade(
            symbol="BTCUSDT",
            action="BUY",
            settlement_date=datetime.now() + timedelta(days=1),
            price=Decimal("30000.00"),
            quantity=1,
            executed_at=datetime.now(),
            order_id=order_id,
        )
        assert trade_id == trade_repo.dao.test_trade.id

    async def test_insert_trade_exception(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta
        from decimal import Decimal
        from uuid import uuid4

        trade_repo._raise_exception = True
        order_id = uuid4()
        with pytest.raises(ValueError) as excinfo:
            trade_repo.insert_trade(
                symbol="BTCUSDT",
                action="BUY",
                settlement_date=datetime.now() + timedelta(days=1),
                price=Decimal("30000.00"),
                quantity=1,
                executed_at=datetime.now(),
                order_id=order_id,
            )
        assert "Database error" in str(excinfo.value)

    async def test_fetch_open_positions_normal(self, trade_repo: TradeRepo):
        positions = trade_repo.fetch_open_positions()
        assert len(positions) == 1
        assert positions[0].user_id == "user_1"
        assert positions[0].account_id == "account_1"

    async def test_fetch_open_positions_empty(self, trade_repo: TradeRepo):
        trade_repo._return_empty = True
        positions = trade_repo.fetch_open_positions()
        assert len(positions) == 0

    async def test_fetch_open_positions_exception(self, trade_repo: TradeRepo):
        trade_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            trade_repo.fetch_open_positions()
        assert "Database error" in str(excinfo.value)

    async def test_fetch_trades_by_date_range_normal(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        trades = trade_repo.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 1
        assert trades[0].id == 1

    async def test_fetch_trades_by_date_range_empty(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta

        trade_repo._return_empty = True
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        trades = trade_repo.fetch_trades_by_date_range(start_date, end_date)
        assert len(trades) == 0

    async def test_fetch_trades_by_date_range_exception(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta

        trade_repo._raise_exception = True
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        with pytest.raises(ValueError) as excinfo:
            trade_repo.fetch_trades_by_date_range(start_date, end_date)
        assert "Database error" in str(excinfo.value)

    async def test_fetch_trades_by_order_id_normal(self, trade_repo: TradeRepo):
        from uuid import UUID

        order_id = UUID("12345678-1234-5678-1234-567812345678")
        trades = trade_repo.fetch_trades_by_order_id(order_id)
        assert len(trades) == 1
        assert trades[0].order_id == order_id

    async def test_fetch_trades_by_order_id_empty(self, trade_repo: TradeRepo):
        from uuid import UUID

        trade_repo._return_empty = True
        order_id = UUID("12345678-1234-5678-1234-567812345678")
        trades = trade_repo.fetch_trades_by_order_id(order_id)
        assert len(trades) == 0

    async def test_fetch_trades_by_order_id_exception(self, trade_repo: TradeRepo):
        from uuid import UUID

        trade_repo._raise_exception = True
        order_id = UUID("12345678-1234-5678-1234-567812345678")
        with pytest.raises(ValueError) as excinfo:
            trade_repo.fetch_trades_by_order_id(order_id)
        assert "Database error" in str(excinfo.value)

    async def test_update_settled_trades_normal(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta

        settlement_datetime = datetime.now() - timedelta(days=1)
        updated_count = trade_repo.update_settled_trades(settlement_datetime)
        assert updated_count == 1

    async def test_update_settled_trades_exception(self, trade_repo: TradeRepo):
        from datetime import datetime, timedelta

        trade_repo._raise_exception = True
        settlement_datetime = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError) as excinfo:
            trade_repo.update_settled_trades(settlement_datetime)
        assert "Database error" in str(excinfo.value)

    async def test_delete_trade_normal(self, trade_repo: TradeRepo):
        from uuid import UUID

        trade_id = UUID("12345678-1234-5678-1234-567812345678")
        deleted_count = trade_repo.delete_trade(trade_id)
        assert deleted_count == 1

    async def test_delete_trade_exception(self, trade_repo: TradeRepo):
        from uuid import UUID

        trade_repo._raise_exception = True
        trade_id = UUID("12345678-1234-5678-1234-567812345678")
        with pytest.raises(ValueError) as excinfo:
            trade_repo.delete_trade(trade_id)
        assert "Database error" in str(excinfo.value)

    async def test_delete_all_trades_normal(self, trade_repo: TradeRepo):
        deleted_count = trade_repo.delete_all_trades()
        assert deleted_count == 1

    async def test_delete_all_trades_exception(self, trade_repo: TradeRepo):
        trade_repo._raise_exception = True
        with pytest.raises(ValueError) as excinfo:
            trade_repo.delete_all_trades()
        assert "Database error" in str(excinfo.value)
