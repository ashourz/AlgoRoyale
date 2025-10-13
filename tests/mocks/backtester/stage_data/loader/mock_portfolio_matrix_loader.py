import pandas as pd

from algo_royale.backtester.stage_data.loader.portfolio_matrix_loader import (
    PortfolioMatrixLoader,
)
from tests.mocks.backtester.data_preparer.mock_asset_matrix_preparer import (
    MockAssetMatrixPreparer,
)
from tests.mocks.backtester.executor.mock_strategy_backtest_executor import (
    MockStrategyBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.loader.mock_stage_data_loader import (
    MockStageDataLoader,
)
from tests.mocks.backtester.strategy_factory.signal.mock_signal_strategy_factory import (
    MockSignalStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioMatrixLoader(PortfolioMatrixLoader):
    def __init__(self):
        self.strategy_backtest_executor = MockStrategyBacktestExecutor()
        self.asset_matrix_preparer = MockAssetMatrixPreparer()
        self.stage_data_manager = MockStageDataManager()
        self.stage_data_loader = MockStageDataLoader()
        self.strategy_factory = MockSignalStrategyFactory()
        self.data_dir = "mock/path"
        self.optimization_root = "mock/opt"
        self.signal_summary_json_filename = "mock_signal_summary.json"
        self.symbol_signals_filename = "mock_symbol_signals.json"
        self.logger = MockLoggable()
        super().__init__(
            strategy_backtest_executor=self.strategy_backtest_executor,
            asset_matrix_preparer=self.asset_matrix_preparer,
            stage_data_manager=self.stage_data_manager,
            stage_data_loader=self.stage_data_loader,
            strategy_factory=self.strategy_factory,
            data_dir=self.data_dir,
            optimization_root=self.optimization_root,
            signal_summary_json_filename=self.signal_summary_json_filename,
            symbol_signals_filename=self.symbol_signals_filename,
            logger=self.logger,
        )
        self.raise_exception = False
        self.return_empty = False
        self.default_portfolio_matrix = pd.DataFrame(
            {"Asset1": [0.5, 0.5], "Asset2": [0.5, 0.5], "Asset3": [0.5, 0.5]}
        )
        self.portfolio_matrix = self.default_portfolio_matrix

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.raise_exception = False
        self.return_empty = False
        self.portfolio_matrix = self.default_portfolio_matrix

    async def get_portfolio_matrix(self, symbols, start_date, end_date):
        if self.raise_exception:
            raise Exception("Mocked exception")
        if self.return_empty:
            return pd.DataFrame()
        return self.portfolio_matrix
