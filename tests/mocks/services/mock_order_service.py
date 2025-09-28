from algo_royale.services.orders_service import OrderService
from tests.mocks.adapters.mock_orders_adapter import MockOrdersAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_order_repo import MockOrderRepo
from tests.mocks.repo.mock_trade_repo import MockTradeRepo


class MockOrderService(OrderService):
    def __init__(self):
        super().__init__(
            orders_adapter=MockOrdersAdapter(),
            order_repo=MockOrderRepo(),
            trade_repo=MockTradeRepo(),
            logger=MockLoggable(),
        )

    def set_return_empty(self, value: bool):
        self.orders_adapter.set_return_empty(value)
        self.order_repo.set_return_empty(value)
        self.trade_repo.set_return_empty(value)

    def reset_return_empty(self):
        self.orders_adapter.reset_return_empty()
        self.order_repo.reset_return_empty()
        self.trade_repo.reset_return_empty()

    def set_raise_exception(self, value: bool):
        self.orders_adapter.set_raise_exception(value)
        self.order_repo.set_raise_exception(value)
        self.trade_repo.set_raise_exception(value)

    def reset_raise_exception(self):
        self.orders_adapter.reset_raise_exception()
        self.order_repo.reset_raise_exception()
        self.trade_repo.reset_raise_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
