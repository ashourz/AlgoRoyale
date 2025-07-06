from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    mockPortfolioStrategyOptimizerFactory,
)
from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)


@pytest.fixture
def mock_loader():
    return MagicMock()


@pytest.fixture
def mock_preparer():
    return MagicMock()


@pytest.fixture
def mock_writer():
    return MagicMock()


@pytest.fixture
def mock_manager(tmp_path):
    mgr = MagicMock()
    # Patch get_directory_path to return a real temp directory
    mgr.get_directory_path.side_effect = (
        lambda base_dir=None,
        stage=None,
        symbol=None,
        strategy_name=None,
        start_date=None,
        end_date=None: tmp_path
        / f"{stage.name if stage else 'default_stage'}_{strategy_name if strategy_name else 'default_strategy'}_{symbol if symbol else 'default_symbol'}"
    )
    return mgr


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_combinator():
    class DummyStrategy:
        __name__ = "DummyStrategy"

        @staticmethod
        def optuna_suggest(trial, prefix=""):
            return {}

        def get_id(self):
            return "DummyStrategy"

    class DummyCombinator:
        @staticmethod
        def all_strategy_combinations(logger=None):
            return [DummyStrategy]

    return DummyCombinator


@pytest.fixture
def mock_executor():
    exec = MagicMock()
    exec.run_backtest.return_value = {"transactions": []}
    return exec


@pytest.fixture
def mock_evaluator():
    eval = MagicMock()
    eval.evaluate.return_value = {PortfolioMetric.SHARPE_RATIO.value: 2.0}
    return eval


@pytest.fixture
def mock_portfolio_strategy_optimizer_factory():
    return mockPortfolioStrategyOptimizerFactory()


@pytest.mark.asyncio
async def test_portfolio_optimization_process(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_combinator,
    mock_executor,
    mock_evaluator,
    mock_portfolio_strategy_optimizer_factory,
):
    optimizer_factory = mock_portfolio_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_value": 2.0,
            "best_params": {},
            "meta": {},
            "metrics": {PortfolioMetric.SHARPE_RATIO.value: 2.0},
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
        asset_matrix_preparer=MagicMock(),  # <-- added
        optimization_json_filename="dummy_optimization.json",
        portfolio_strategy_optimizer_factory=optimizer_factory,
    )

    coordinator.start_date = "2021-01-01"
    coordinator.end_date = "2021-12-31"
    coordinator.window_id = "window_1"

    # Simulate prepared data
    async def df_iter():
        yield pd.DataFrame({"a": [1, 2, 3]})

    prepared_data = {"AAPL": lambda: df_iter()}
    results = await coordinator._process_and_write(data=prepared_data)
    print("DEBUG:RESULTS", results)
    assert "AAPL" in results
    assert "DummyStrategy" in results["AAPL"]
    assert "window_1" in results["AAPL"]["DummyStrategy"]
    assert "metrics" in results["AAPL"]["DummyStrategy"]["window_1"]
    assert (
        results["AAPL"]["DummyStrategy"]["window_1"]["metrics"][
            PortfolioMetric.SHARPE_RATIO.value
        ]
        == 2.0
    )
