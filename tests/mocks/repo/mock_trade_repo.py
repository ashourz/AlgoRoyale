from datetime import datetime
from uuid import UUID

from algo_royale.models.db.db_position import DBPosition
from algo_royale.models.db.db_trade import DBTrade
from algo_royale.repo.trade_repo import TradeRepo
from tests.mocks.clients.db.mock_trade_dao import MockTradeDAO
from tests.mocks.mock_loggable import MockLoggable


class MockTradeRepo(TradeRepo):
    def __init__(self):
        self.dao = MockTradeDAO()
        self.logger = MockLoggable()
        super().__init__(
            dao=self.dao, logger=self.logger, user_id="user_1", account_id="account_1"
        )
        self._return_empty = False
        self._raise_exception = False

    def set_return_empty(self, value: bool):
        self._return_empty = value

    def reset_return_empty(self):
        self._return_empty = False

    def set_raise_exception(self, value: bool):
        self._raise_exception = value

    def reset_raise_exception(self):
        self._raise_exception = False

    def reset_dao(self):
        self.dao.reset()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
        self.reset_dao()

    def fetch_unsettled_trades(
        self, limit: int = 100, offset: int = 0
    ) -> list[DBTrade]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_unsettled_trades(limit, offset)

    def insert_trade(
        self,
        external_id: str,
        symbol: str,
        action: str,
        settlement_date: datetime,
        price: float,
        quantity: float,
        executed_at: datetime,
        order_id: UUID,
    ) -> UUID | None:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.insert_trade(
            external_id=external_id,
            symbol=symbol,
            action=action,
            settlement_date=settlement_date,
            price=price,
            quantity=quantity,
            executed_at=executed_at,
            order_id=order_id,
            user_id=self.user_id,
            account_id=self.account_id,
        )

    def fetch_open_positions(self) -> list[DBPosition]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_open_positions(self.user_id, self.account_id)

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBTrade]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_trades_by_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    def fetch_trades_by_order_id(self, order_id: UUID) -> list[DBTrade]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_trades_by_order_id(order_id=order_id)

    def update_settled_trades(self, settlement_datetime: datetime) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.update_settled_trades(settlement_datetime)

    def delete_trade(self, trade_id: UUID) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.delete_trade(trade_id)

    def delete_all_trades(self) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.delete_all_trades()
