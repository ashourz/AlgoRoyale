from algo_royale.adapters.trading.account_adapter import AccountAdapter
from tests.mocks.clients.alpaca.mock_alpaca_account_client import (
    MockAlpacaAccountClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAccountAdapter(AccountAdapter):
    def __init__(self):
        client = MockAlpacaAccountClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.account_client.return_empty = value

    def reset_return_empty(self):
        self.account_client.return_empty = False

    def set_raise_exception(self, value: bool):
        self.account_client.raise_exception = value

    def reset_raise_exception(self):
        self.account_client.raise_exception = False

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
