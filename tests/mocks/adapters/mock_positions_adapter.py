from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from tests.mocks.clients.mock_alpaca_positions_client import MockAlpacaPositionsClient
from tests.mocks.mock_loggable import MockLoggable


class MockPositionsAdapter(PositionsAdapter):
    def __init__(self):
        client = MockAlpacaPositionsClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_positions(self, *args, **kwargs):
        if self.return_empty:
            return []
        return [{"symbol": "AAPL", "qty": 10}]
