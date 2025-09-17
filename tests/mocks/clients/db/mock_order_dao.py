from datetime import datetime
from uuid import UUID

from algo_royale.clients.db.dao.order_dao import OrderDAO
from algo_royale.models.db.db_order import DBOrder


class MockOrderDAO(OrderDAO):
    def __init__(self):
        self.base_order = DBOrder(
            id=UUID("123e4567-e89b-12d3-a456-426614174001"),
            symbol="AAPL",
            market="stocks",
            settled=False,
            order_type="market",
            status="open",
            action="buy",
            notional=1000.0,
            quantity=10,
            price=100.0,
            user_id="user_1",
            account_id="account_1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.test_order = self.base_order

    def reset_order(self):
        self.test_order = self.base_order

    def reset(self):
        self.reset_order()

    def fetch_order_by_id(
        self, order_id: UUID, user_id: str, account_id: str
    ) -> list[DBOrder]:
        return [self.test_order]

    def fetch_all_orders_by_status(self, status_list: list[str]) -> list[DBOrder]:
        return [self.test_order]

    def fetch_orders_by_status(
        self, status_list: list[str], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        return [self.test_order]

    def fetch_all_orders_by_symbol_and_status(
        self, status_list: list[str], status: str
    ) -> list[DBOrder]:
        return [self.test_order]

    def fetch_orders_by_symbol_and_status(
        self, symbol: str, status_list: list[str], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        return [self.test_order]

    def fetch_unsettled_orders(self) -> list[DBOrder]:
        return [self.test_order]

    def insert_order(
        self,
        symbol: str,
        order_type: str,
        status: str,
        action: str,
        notional: float | None,
        quantity: int | None,
        price: float | None,
        user_id: str,
        account_id: str,
    ) -> str:
        # Return a unique string order ID based on symbol and notional for test realism
        return f"mock_order_{symbol}_{notional or ''}"

    def update_order(
        self, order_id: UUID, status: str, quantity: int, price: float
    ) -> int:
        return 1

    def update_order_as_settled(self, order_id: UUID) -> int:
        return 1

    def delete_order(self, order_id: UUID) -> int:
        return 1

    def delete_all_orders(self) -> int:
        return 1
