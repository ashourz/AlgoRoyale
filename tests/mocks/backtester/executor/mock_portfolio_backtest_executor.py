from typing import Any, Dict

import pandas as pd

from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioBacktestExecutor(PortfolioBacktestExecutor):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(logger=self.logger)
        self.raise_exception = False
        self.return_none = False
        self.backtest_result = {"mock": True}

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def set_return_none(self, value: bool):
        self.return_none = value

    def set_result(self, value):
        self.result = value

    def reset(self):
        self.raise_exception = False
        self.return_none = False
        self.result = {"mock": True}

    def reset_raise_exception(self):
        self.raise_exception = False

    async def async_run_backtest(
        self,
        strategy: BasePortfolioStrategy,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        if self.raise_exception:
            raise Exception("Mocked exception in run_backtest")
        return self.backtest_result
