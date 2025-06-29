from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
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
    class Manager:
        def get_directory_path(self):
            return tmp_path

        def get_extended_path(self, **kwargs):
            return tmp_path

    return Manager()


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


@pytest.mark.asyncio
async def test_portfolio_optimization_process(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_combinator,
    mock_executor,
    mock_evaluator,
):
    coordinator = PortfolioOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[mock_combinator],
        executor=mock_executor,
        evaluator=mock_evaluator,
        optimization_root=mock_manager.get_directory_path(),
        asset_matrix_preparer=MagicMock(),  # <-- added
        optimization_json_filename="dummy_optimization.json",
    )

    coordinator.start_date = "2021-01-01"
    coordinator.end_date = "2021-12-31"
    coordinator.window_id = "window_1"

    # Simulate prepared data
    async def df_iter():
        yield pd.DataFrame({"a": [1, 2, 3]})

    prepared_data = {"AAPL": lambda: df_iter()}
    results = await coordinator.process(prepared_data=prepared_data)
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
