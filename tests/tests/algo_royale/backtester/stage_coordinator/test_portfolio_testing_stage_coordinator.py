import json
import time
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
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

        def __init__(self, a=1):
            pass

        @staticmethod
        def optuna_suggest(trial, prefix=""):
            return {}

    class DummyFactory:
        func = DummyStrategy

    class DummyCombinator:
        @staticmethod
        def all_strategy_combinations(**kwargs):
            return [DummyFactory]

    return DummyCombinator


@pytest.fixture
def mock_executor():
    exec = MagicMock()
    exec.run_backtest.return_value = {
        "transactions": [],
        "portfolio_returns": [0.01, 0.02, 0.03],  # Required by coordinator
    }
    return exec


@pytest.fixture
def mock_evaluator():
    eval = MagicMock()
    eval.evaluate.return_value = {"sharpe": 2.0}
    return eval


@pytest.fixture
def mock_asset_matrix_preparer():
    mock = MagicMock()
    mock.prepare.return_value = pd.DataFrame(
        {
            "AAPL": [100, 101, 102],
            "GOOG": [200, 202, 204],
        }
    )
    return mock


@pytest.mark.asyncio
async def test_portfolio_testing_process(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_combinator,
    mock_executor,
    mock_evaluator,
    mock_asset_matrix_preparer,
):
    # Prepare fake optimization result file for train window
    train_start = datetime(2021, 1, 1)
    train_end = datetime(2021, 12, 31)
    test_start = datetime(2022, 1, 1)
    test_end = datetime(2022, 12, 31)
    train_window_id = f"{train_start.strftime('%Y%m%d')}_{train_end.strftime('%Y%m%d')}"
    tmp_path = mock_manager.get_directory_path.return_value

    # Now this will match what the coordinator expects
    opt_json_path = tmp_path / "test_opt.json"
    opt_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(opt_json_path, "w") as f:
        json.dump(
            {train_window_id: {"optimization": {"best_params": {"a": 1}}}},
            f,
        )
    time.sleep(0.05)

    coordinator = PortfolioTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[mock_combinator],
        executor=mock_executor,
        evaluator=mock_evaluator,
        optimization_root=tmp_path,
        optimization_json_filename="test_opt.json",
        asset_matrix_preparer=mock_asset_matrix_preparer,
    )

    async def df_iter():
        yield pd.DataFrame(
            {
                "AAPL": [100, 101, 102],
                "GOOG": [200, 202, 204],
            }
        )

    prepared_data = {"AAPL": lambda: df_iter()}
    coordinator.train_start_date = train_start
    coordinator.train_end_date = train_end
    coordinator.train_window_id = train_window_id
    coordinator.test_start_date = test_start
    coordinator.test_end_date = test_end
    coordinator.test_window_id = (
        f"{test_start.strftime('%Y%m%d')}_{test_end.strftime('%Y%m%d')}"
    )

    # Mock _get_optimization_results to return valid data
    coordinator._get_optimization_results = (
        lambda strategy_name, symbol, start_date, end_date: {
            train_window_id: {"optimization": {"best_params": {"a": 1}}}
        }
    )

    results = await coordinator._process(prepared_data=prepared_data)
    print("DEBUG RESULTS:", results)
    mock_evaluator.evaluate.assert_called()
    assert "AAPL" in results
    assert "DummyStrategy" in results["AAPL"]
    assert coordinator.test_window_id in results["AAPL"]["DummyStrategy"]
    assert results["AAPL"]["DummyStrategy"][coordinator.test_window_id]["sharpe"] == 2.0
