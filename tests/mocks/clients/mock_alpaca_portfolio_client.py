from datetime import datetime

from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import (
    AlpacaPortfolioClient,
)
from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaPortfolioClient(AlpacaPortfolioClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        self.return_empty = False
        self.throw_exception = False

    async def fetch_portfolio_history(self, period="1M", timeframe="1D", **kwargs):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaPortfolioClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            tf = timeframe or "1D"
            return PortfolioPerformance(
                timestamp=[],
                equity=[],
                profit_loss=[],
                profit_loss_pct=[],
                base_value=0.0,
                timeframe=tf,
                base_value_asof=datetime.now(),
            )
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
