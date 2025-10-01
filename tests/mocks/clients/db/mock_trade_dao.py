from datetime import datetime
from decimal import Decimal
from uuid import UUID

from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.models.db.db_position import DBPosition
from algo_royale.models.db.db_trade import DBTrade


class MockTradeDAO(TradeDAO):
    def __init__(self):
        self.base_trade = DBTrade(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            external_id="mocked_external_id_002",
            user_id="user_1",
            account_id="account_1",
            symbol="BTCUSDT",
            action="buy",
            settled=False,
            settlement_date=datetime.now(),
            price=Decimal("40000.00"),
            quantity=1,
            executed_at=datetime.now(),
            created_at=datetime.now(),
            order_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            updated_at=datetime.now(),
        )
        self.base_open_position = DBPosition(
            symbol="BTCUSDT",
            market="crypto",
            user_id="user_1",
            account_id="account_1",
            net_position=1.0,
        )
        self.test_trade = self.base_trade
        self.test_open_position = self.base_open_position

    def reset_trade(self):
        self.test_trade = self.base_trade

    def reset_open_position(self):
        self.test_open_position = self.base_open_position

    def reset(self):
        self.reset_trade()
        self.reset_open_position()

    def fetch_unsettled_trades(
        self, limit: int = 100, offset: int = 0
    ) -> list[DBTrade]:
        return [self.test_trade.model_copy(update={"id": 1, "settled": False})]

    def fetch_open_positions(self, user_id, account_id) -> list[DBPosition]:
        return [
            self.test_open_position.model_copy(
                update={"user_id": user_id, "account_id": account_id}
            )
        ]

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBTrade]:
        return [
            self.test_trade.model_copy(
                update={
                    "id": 1,
                    "executed_at": start_date,
                    "settled": True,
                    "settlement_date": end_date,
                    "created_at": start_date,
                    "updated_at": end_date,
                }
            )
        ]

    def fetch_trades_by_order_id(self, order_id: UUID) -> list[DBTrade]:
        return [self.test_trade.model_copy(update={"order_id": order_id})]

    def insert_trade(
        self,
        external_id: str,
        symbol: str,
        action: str,
        settlement_date: datetime,
        price: Decimal,
        quantity: int,
        executed_at: datetime,
        order_id: UUID,
        user_id: str,
        account_id: str,
    ) -> UUID | None:
        return self.test_trade.id

    def update_settled_trades(self, settlement_datetime: datetime) -> int:
        return 1

    def delete_trade(self, trade_id: UUID) -> int:
        return 1

    def delete_all_trades(self) -> int:
        return 1
