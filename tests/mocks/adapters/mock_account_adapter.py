from algo_royale.adapters.trading.account_adapter import AccountAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockAccountAdapter(AccountAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_account(self, *args, **kwargs):
        if self.return_empty:
            return None
        return {"id": "test_account", "balance": 1000.0}
