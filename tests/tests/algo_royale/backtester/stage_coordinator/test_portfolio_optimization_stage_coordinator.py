import pandas as pd
import pytest

from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_portfolio_backtest_evaluator import (
    MockPortfolioBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_portfolio_backtest_executor import (
    MockPortfolioBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.optimizer.portfolio.mock_portfolio_strategy_optimizer_factory import (
    MockPortfolioStrategyOptimizerFactory,
)
from tests.mocks.backtester.stage_data.loader.mock_symbol_strategy_data_loader import (
    MockSymbolStrategyDataLoader,
)
from tests.mocks.backtester.strategy_factory.portfolio.mock_portfolio_strategy_combinator_factory import (
    MockPortfolioStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def mock_loader():
    return MockSymbolStrategyDataLoader()


@pytest.fixture
def mock_manager(tmp_path):
    mgr = MockStageDataManager()
    mgr.get_directory_path = lambda *a, **k: tmp_path
    return mgr


@pytest.fixture
def mock_logger():
    return MockLoggable()


@pytest.fixture
def mock_combinator():
    return MockPortfolioStrategyCombinatorFactory()


@pytest.fixture
def mock_executor():
    return MockPortfolioBacktestExecutor()


@pytest.fixture
def mock_evaluator():
    return MockPortfolioBacktestEvaluator()


@pytest.fixture
def mock_portfolio_strategy_optimizer_factory():
    return MockPortfolioStrategyOptimizerFactory()


@pytest.fixture
def mock_asset_matrix_preparer():
    class MockAssetMatrixPreparer:
        def prepare(self, *args, **kwargs):
            return pd.DataFrame(
                {
                    "price": [100, 101, 102],
                    "volume": [1000, 1100, 1200],
                    "returns": [0.01, 0.02, 0.03],
                }
            )

    return MockAssetMatrixPreparer()


@pytest.mark.asyncio
async def test_portfolio_optimization_process(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_combinator,
    mock_executor,
    mock_evaluator,
    mock_portfolio_strategy_optimizer_factory,
    mock_asset_matrix_preparer,
):
    optimizer_factory = mock_portfolio_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_value": 2.0,
            "best_params": {},
            "meta": {
                "run_time_sec": 10,
                "n_trials": 100,
                "symbol": "AAPL",
                "direction": "long",
                "multi_objective": False,
            },
            "metrics": {PortfolioMetric.SHARPE_RATIO.value: 2.0},
            "window": {"start_date": "2021-01-01", "end_date": "2021-12-31"},
        }
    )
    coordinator = PortfolioOptimizationStageCoordinator(
        data_loader=mock_loader,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[mock_combinator],
        executor=mock_executor,
        evaluator=mock_evaluator,
        optimization_root=mock_manager.get_directory_path(),
        asset_matrix_preparer=mock_asset_matrix_preparer,
    )
    # Simulate data input and run outward-facing method(s) as needed
    # Add error/exception handling tests as follow-up
