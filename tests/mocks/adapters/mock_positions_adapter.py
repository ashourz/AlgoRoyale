from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from tests.mocks.clients.alpaca.mock_alpaca_positions_client import (
    MockAlpacaPositionsClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPositionsAdapter(PositionsAdapter):
    def __init__(self):
        client = MockAlpacaPositionsClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)

    def set_return_empty(self, value: bool):
        self.client.return_empty = value

    def reset_return_empty(self):
        self.client.return_empty = False

    def set_raise_exception(self, value: bool):
        self.client.raise_exception = value

    def reset_raise_exception(self):
        self.client.raise_exception = False
