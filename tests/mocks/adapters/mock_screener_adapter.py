from algo_royale.adapters.market_data.screener_adapter import ScreenerAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockScreenerAdapter(ScreenerAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_screened_symbols(self, *args, **kwargs):
        if self.return_empty:
            return []
        return ["AAPL", "GOOG"]
