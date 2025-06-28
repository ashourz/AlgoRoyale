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
    m = MagicMock()
    m.get_directory_path.return_value = tmp_path
    return m


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_combinator():
    class DummyStrategy:
        __name__ = "DummyStrategy"

        def __init__(self):
            pass

        @staticmethod
        def optuna_suggest(trial, prefix=""):
            return {}

    class DummyCombinator:
        @staticmethod
        def all_strategy_combinations():
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
    eval.evaluate.return_value = {"sharpe": 2.0}
    return eval


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
):
    # Prepare fake optimization result file for train window
    train_start = datetime(2021, 1, 1)
    train_end = datetime(2021, 12, 31)
    test_start = datetime(2022, 1, 1)
    test_end = datetime(2022, 12, 31)
    train_window_id = f"{train_start.strftime('%Y%m%d')}_{train_end.strftime('%Y%m%d')}"
    tmp_path = mock_manager.get_directory_path.return_value
    opt_json_path = tmp_path / "test_opt.json"
    opt_json_path.parent.mkdir(parents=True, exist_ok=True)
    import json

    with open(opt_json_path, "w") as f:
        json.dump({train_window_id: {"optimization": {"best_params": {}}}}, f)

    coordinator = PortfolioTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[mock_combinator],
        executor=mock_executor,
        evaluator=mock_evaluator,
        optimization_root=tmp_path,  # <-- added
        optimization_json_filename="test_opt.json",
        asset_matrix_preparer=MagicMock(),  # <-- added
    )

    # Simulate prepared data
    async def df_iter():
        yield pd.DataFrame({"a": [1, 2, 3]})

    prepared_data = {"AAPL": lambda: df_iter()}
    coordinator.train_start_date = train_start
    coordinator.train_end_date = train_end
    coordinator.train_window_id = train_window_id
    coordinator.test_start_date = test_start
    coordinator.test_end_date = test_end
    coordinator.test_window_id = (
        f"{test_start.strftime('%Y%m%d')}_{test_end.strftime('%Y%m%d')}"
    )
    results = await coordinator.process(prepared_data=prepared_data)
    assert "AAPL" in results
    assert "DummyStrategy" in results["AAPL"]
    assert coordinator.test_window_id in results["AAPL"]["DummyStrategy"]
    assert results["AAPL"]["DummyStrategy"][coordinator.test_window_id]["sharpe"] == 2.0
