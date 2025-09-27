from uuid import UUID

from algo_royale.models.db.db_order import DBOrder
from algo_royale.repo.order_repo import DBOrderStatus, OrderAction, OrderRepo, OrderType
from tests.mocks.clients.db.mock_order_dao import MockOrderDAO
from tests.mocks.mock_loggable import MockLoggable


class MockOrderRepo(OrderRepo):
    def __init__(self):
        self.dao = MockOrderDAO()
        self.logger = MockLoggable()
        self.user_id = "user_1"
        self.account_id = "account_1"
        super().__init__(dao=self.dao, logger=self.logger)
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

    def fetch_order_by_id(self, order_id: UUID) -> list[DBOrder]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_order_by_id(order_id, self.user_id, self.account_id)

    def fetch_orders_by_status(
        self, status_list: list[DBOrderStatus], limit: int = 100, offset: int = 0
    ) -> list[DBOrder]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_orders_by_status(status_list, limit, offset)

    def fetch_all_orders_by_symbol_and_status(
        self, symbol: str, status_list: list[DBOrderStatus]
    ) -> list[DBOrder]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_orders_by_symbol_and_status(symbol, status_list)

    def fetch_orders_by_symbol_and_status(
        self,
        symbol: str,
        status_list: list[DBOrderStatus],
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBOrder]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_orders_by_symbol_and_status(
            symbol, status_list, limit, offset
        )

    def fetch_unsettled_orders(self) -> list[DBOrder]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_unsettled_orders()

    def insert_order(
        self,
        symbol: str,
        order_type: OrderType,
        status: DBOrderStatus,
        action: OrderAction,
        notional: float | None = None,
        quantity: int | None = None,
        price: float | None = None,
    ) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.insert_order(
            symbol,
            order_type,
            status,
            action,
            notional,
            quantity,
            price,
            self.user_id,
            self.account_id,
        )

    def update_order(
        self,
        order_id: UUID,
        new_status: DBOrderStatus,
        quantity: int | None,
        price: float | None,
    ) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return 0
        return self.dao.update_order(order_id, new_status, quantity, price)

    def update_order_as_settled(self, order_id: UUID) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return 0
        return self.dao.update_order_as_settled(order_id)

    def delete_order(self, order_id: UUID) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return 0
        return self.dao.delete_order(order_id)

    def delete_all_orders(self) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return 0
        return self.dao.delete_all_orders()
