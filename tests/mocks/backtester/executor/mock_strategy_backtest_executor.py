from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.mock_loggable import MockLoggable


class MockStrategyBacktestExecutor(StrategyBacktestExecutor):
    def reset_raise_exception(self):
        self.raise_exception = False

    def reset_return_none(self):
        self.return_none = False

    def __init__(self):
        self.stage_data_manager = MockStageDataManager()
        self.logger = MockLoggable()
        super().__init__(stage_data_manager=self.stage_data_manager, logger=self.logger)
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

    async def async_run_backtest(
        self,
        strategies: list[BaseSignalStrategy],
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ) -> Dict[str, list[pd.DataFrame]]:
        if self.raise_exception:
            raise Exception("Mocked exception in run_backtest")
        return self.backtest_result
