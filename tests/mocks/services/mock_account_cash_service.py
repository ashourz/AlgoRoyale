from algo_royale.services.account_cash_service import AccountCashService
from tests.mocks.adapters.mock_account_cash_adapter import MockAccountCashAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockAccountCashService(AccountCashService):
    def __init__(self):
        super().__init__(
            cash_adapter=MockAccountCashAdapter(),
            logger=MockLoggable(),
        )

    def set_raise_exception(self, value: bool):
        self.cash_adapter.set_raise_exception(value)

    def reset_raise_exception(self):
        self.cash_adapter.reset_raise_exception()

    def reset(self):
        self.reset_raise_exception()
