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

    def set_return_empty(self, value: bool):
        self.account_adapter.set_return_empty(value)

    def reset_return_empty(self):
        self.account_adapter.reset_return_empty()

    def set_raise_exception(self, value: bool):
        self.account_adapter.set_raise_exception(value)

    def reset_raise_exception(self):
        self.account_adapter.reset_raise_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
