from datetime import timedelta
from uuid import UUID

from algo_royale.models.db.db_trade import DBTrade
from algo_royale.services.trades_service import TradesService
from tests.mocks.adapters.mock_account_adapter import MockAccountAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_trade_repo import MockTradeRepo


class MockTradesService(TradesService):
    def __init__(self):
        super().__init__(
            account_adapter=MockAccountAdapter(),
            trade_repo=MockTradeRepo(),
            logger=MockLoggable(),
            user_id="user_1",
            account_id="account_1",
            days_to_settle=1,
        )
        self.return_empty = False
        self.raise_exception = False
        self.base_trades: list[DBTrade] = [
            DBTrade(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                user_id="user_1",
                account_id="account_1",
                symbol="AAPL",
                action="buy",
                settled=True,
                settlement_date="2023-10-01",
                quantity=10,
                price=150.0,
                executed_at="2023-10-01T10:00:00Z",
                created_at="2023-10-01T10:00:00Z",
                order_id=UUID("00000000-0000-0000-0000-000000000002"),
                updated_at="2023-10-01T10:00:00Z",
            )
        ]
        self.trades = self.base_trades.copy()

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.account_adapter.reset()
        self.repo.reset()
        self.trades = self.base_trades.copy()

    def fetch_trades_by_order_id(self, order_id):
        if self.raise_exception:
            raise ValueError("Database error")
        if self.return_empty:
            return []
        return [
            trade.model_copy(update={"order_id": order_id}) for trade in self.trades
        ]

    def fetch_unsettled_trades(self, limit=100, offset=0):
        if self.raise_exception:
            raise ValueError("Database error")
        if self.return_empty:
            return []
        return [trade.model_copy(update={"settled": False}) for trade in self.trades]

    def update_settled_trades(self):
        return

    def insert_trade(
        self,
        symbol: str,
        action: str,
        settled: bool,
        settlement_date: str,
        quantity: int,
        price: float,
        executed_at: str,
    ) -> str:
        if self.raise_exception:
            raise ValueError("Database error")
        new_trade = DBTrade(
            id=UUID("00000000-0000-0000-0000-000000000003"),
            user_id=self.user_id,
            account_id=self.account_id,
            symbol=symbol,
            action=action,
            settled=settled,
            settlement_date=settlement_date,
            quantity=quantity,
            price=price,
            executed_at=executed_at,
            created_at="2023-10-01T10:00:00Z",
            order_id=UUID("00000000-0000-0000-0000-000000000002"),
            updated_at="2023-10-01T10:00:00Z",
        )
        self.trades.append(new_trade)
        return str(new_trade.id)

    def fetch_trades_by_date_range(self, start_date, end_date, limit=100, offset=0):
        if self.raise_exception:
            raise ValueError("Database error")
        if self.return_empty:
            return []
        return [
            trade.model_copy(
                update={
                    "settled": False,
                    "created_at": start_date,
                    "executed_at": start_date,
                    "settlement_date": start_date + timedelta(days=self.days_to_settle),
                    "updated_at": start_date,
                }
            )
            for trade in self.trades
        ]

    def delete_trade(self, trade_id: UUID) -> int:
        if self.raise_exception:
            raise ValueError("Database error")
        if self.return_empty:
            return 0
        return 1

    def delete_all_trades(self) -> int:
        if self.raise_exception:
            raise ValueError("Database error")
        count = len(self.trades)
        self.trades = []
        return count

    def reconcile_trades(self, start_date, end_date, rerun=True):
        return
