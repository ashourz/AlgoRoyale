from algo_royale.adapters.trading.portfolio_adapter import PortfolioAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioAdapter(PortfolioAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_portfolio(self, *args, **kwargs):
        if self.return_empty:
            return None
        return {"portfolio_value": 10000.0}
