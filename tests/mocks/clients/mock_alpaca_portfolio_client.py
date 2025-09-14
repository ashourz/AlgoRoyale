from datetime import datetime

from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaPortfolioClient:
    def __init__(self):
        self.logger = MockLoggable()

    async def fetch_portfolio_history(self, period="1M", timeframe="1D"):
        return PortfolioPerformance(
            timestamp=[1, 2, 3],
            equity=[1000.0, 1010.0, 1020.0],
            profit_loss=[0.0, 10.0, 20.0],
            profit_loss_pct=[0.0, 0.01, 0.02],
            base_value=1000.0,
            timeframe="1D",
            base_value_asof=datetime.now(),
        )

    async def aclose(self):
        pass
