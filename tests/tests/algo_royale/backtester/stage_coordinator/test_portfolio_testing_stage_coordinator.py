import json
import time
from datetime import datetime

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_portfolio_backtest_evaluator import (
    MockPortfolioBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_portfolio_backtest_executor import (
    MockPortfolioBacktestExecutor,
)
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
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
async def test_portfolio_testing_process(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_combinator,
    mock_executor,
    mock_evaluator,
    mock_asset_matrix_preparer,
):
    train_start = datetime(2021, 1, 1)
    train_end = datetime(2021, 12, 31)
    test_start = datetime(2022, 1, 1)
    test_end = datetime(2022, 12, 31)
    train_window_id = f"{train_start.strftime('%Y%m%d')}_{train_end.strftime('%Y%m%d')}"
    tmp_path = mock_manager.get_directory_path()

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

    coordinator._get_optimization_results = (
        lambda strategy_name, symbol, start_date, end_date: {
            coordinator.train_window_id: {
                "optimization": {
                    "best_params": {"a": 1},
                    "metrics": {"sharpe": 2.0},
                },
                "window": {
                    "start_date": train_start.strftime("%Y-%m-%d"),
                    "end_date": train_end.strftime("%Y-%m-%d"),
                },
            }
        }
    )

    results = await coordinator._process_and_write(data=prepared_data)
    assert "AAPL" in results
    assert "DummyStrategy" in results["AAPL"]
    assert coordinator.test_window_id in results["AAPL"]["DummyStrategy"]
    assert (
        results["AAPL"]["DummyStrategy"][coordinator.test_window_id]["metrics"][
            "sharpe"
        ]
        == 2.0
    )
