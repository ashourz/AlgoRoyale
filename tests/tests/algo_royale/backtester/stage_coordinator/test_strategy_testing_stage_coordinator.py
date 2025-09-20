from datetime import datetime
from unittest import mock

import pandas as pd
import pytest

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.testing.signal_strategy_testing_stage_coordinator import (
    SignalStrategyTestingStageCoordinator,
)
from tests.mocks.backtester.evaluator.backtest.mock_signal_backtest_evaluator import (
    MockSignalBacktestEvaluator,
)
from tests.mocks.backtester.executor.mock_strategy_backtest_executor import (
    MockStrategyBacktestExecutor,
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
def mock_logger():
    return MockLoggable()


@pytest.fixture
def mock_manager():
    return MockStageDataManager()


@pytest.fixture
def mock_executor():
    return MockStrategyBacktestExecutor()


@pytest.fixture
def mock_evaluator():
    return MockSignalBacktestEvaluator()


@pytest.fixture
def mock_factory():
    class DummyFactory:
        def build_strategy(self, *args, **kwargs):
            class DummyStrategy:
                pass

            return DummyStrategy()

    return DummyFactory()


@pytest.fixture
def mock_combinator_factory():
    return MockPortfolioStrategyCombinatorFactory()


def test_init_success(
    mock_loader,
    mock_manager,
    mock_executor,
    mock_evaluator,
    mock_factory,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    # Patch BacktestStage.STRATEGY_TESTING to have output_stage
    with mock.patch.object(
        BacktestStage.STRATEGY_TESTING,
        "output_stage",
        create=True,
        new=None,
    ):
        SignalStrategyTestingStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            strategy_factory=mock_factory,
            logger=mock_logger,
            strategy_combinator_factory=[DummyCombinator],
            optimization_root=".",
            optimization_json_filename="test.json",
        )


@pytest.mark.asyncio
async def test_process_returns_metrics(
    mock_loader,
    mock_manager,
    mock_executor,
    mock_evaluator,
    mock_factory,
    mock_logger,
    tmp_path,
):
    """Test that _process_and_write correctly processes valid data and returns expected results."""

    class DummyStrategy:
        __name__ = "StrategyA"

    class DummyCombinator:
        strategy_class = DummyStrategy

    # Prepare a fake optimization_result.json with best_params
    opt_dir = tmp_path / "optimization_StrategyA_AAPL"
    opt_dir.mkdir(parents=True, exist_ok=True)
    opt_path = opt_dir / "test.json"
    train_window_id = "20240101_20240131"
    test_window_id = "20240201_20240228"
    with open(opt_path, "w") as f:
        import json

        json.dump(
            {
                train_window_id: {
                    "optimization": {
                        "strategy": "StrategyA",
                        "best_value": 0.95,
                        "best_params": {
                            "entry_conditions": [{"condition": "entry_condition_1"}],
                            "exit_conditions": [{"condition": "exit_condition_1"}],
                            "trend_conditions": [{"condition": "trend_condition_1"}],
                        },
                        "meta": {
                            "run_time_sec": 10.5,
                            "n_trials": 100,
                            "symbol": "AAPL",
                            "direction": "maximize",
                        },
                        "metrics": {
                            "total_return": 0.15,
                            "sharpe_ratio": 2.0,
                            "win_rate": 0.6,
                            "max_drawdown": -0.1,
                        },
                    },
                    "window": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-31",
                    },
                }
            },
            f,
        )

    StrategyA = type("StrategyA", (), {})
    CombA = type("CombA", (), {"strategy_class": StrategyA})
    coordinator = SignalStrategyTestingStageCoordinator(
        data_loader=mock_loader,
        stage_data_manager=mock_manager,
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[CombA],
        optimization_root=tmp_path,  # Use the temp directory for optimization_root
        optimization_json_filename="test.json",
    )
    coordinator.train_window_id = train_window_id
    coordinator.test_window_id = test_window_id
    coordinator.train_start_date = datetime(2024, 1, 1)
    coordinator.train_end_date = datetime(2024, 1, 31)
    coordinator.test_start_date = datetime(2024, 2, 1)
    coordinator.test_end_date = datetime(2024, 2, 28)

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}
    mock_factory.build_strategy.return_value = StrategyA()
    mock_executor.run_backtest.return_value = {"AAPL": [pd.DataFrame({"result": [1]})]}
    mock_evaluator.evaluate.return_value = {
        "total_return": 0.15,
        "sharpe_ratio": 2.0,
        "win_rate": 0.6,
        "max_drawdown": -0.1,
    }

    # Mock _get_optimization_results to return valid data
    coordinator._get_train_optimization_results = (
        lambda strategy_name, symbol, start_date, end_date: {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "StrategyA",
                    "best_value": 0.95,
                    "best_params": {
                        "entry_conditions": [{"condition": "entry_condition_1"}],
                        "exit_conditions": [{"condition": "exit_condition_1"}],
                        "trend_conditions": [{"condition": "trend_condition_1"}],
                    },
                    "meta": {
                        "run_time_sec": 10.5,
                        "n_trials": 100,
                        "symbol": "AAPL",
                        "direction": "maximize",
                    },
                    "metrics": {
                        "total_return": 0.15,
                        "sharpe_ratio": 2.0,
                        "win_rate": 0.6,
                        "max_drawdown": -0.1,
                    },
                },
            },
        }
    )

    coordinator._get_test_optimization_results = (
        lambda strategy_name, symbol, start_date, end_date: {
            "20240201_20240228": {
                "test": {
                    "metrics": {
                        "total_return": 0.15,
                        "sharpe_ratio": 2.0,
                        "win_rate": 0.6,
                        "max_drawdown": -0.1,
                    },
                    "transactions": [],
                },
                "optimization": {
                    "strategy": "StrategyA",
                    "best_value": 0.95,
                    "best_params": {
                        "entry_conditions": [{"condition": "entry_condition_1"}],
                        "exit_conditions": [{"condition": "exit_condition_1"}],
                        "trend_conditions": [{"condition": "trend_condition_1"}],
                    },
                    "meta": {
                        "run_time_sec": 10.5,
                        "n_trials": 100,
                        "symbol": "AAPL",
                        "direction": "maximize",
                    },
                    "metrics": {
                        "total_return": 0.15,
                        "sharpe_ratio": 2.0,
                        "win_rate": 0.6,
                        "max_drawdown": -0.1,
                    },
                },
                "window": {
                    "start_date": "2024-02-01",
                    "end_date": "2024-02-28",
                },
            },
        }
    )

    result = await coordinator._process_and_write(prepared_data)

    # Validate the structure and content of the results dictionary
    assert "AAPL" in result
    assert "StrategyA" in result["AAPL"]
    assert test_window_id in result["AAPL"]["StrategyA"]
    metrics = result["AAPL"]["StrategyA"][test_window_id]["metrics"]
    assert metrics["total_return"] == 0.15
    assert metrics["sharpe_ratio"] == 2.0
    assert metrics["win_rate"] == 0.6
    assert metrics["max_drawdown"] == -0.1


@pytest.mark.asyncio
async def test_process_warns_on_missing_optimization(
    mock_loader,
    mock_manager,
    mock_executor,
    mock_evaluator,
    mock_factory,
    mock_logger,
    tmp_path,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    with mock.patch.object(
        BacktestStage.STRATEGY_TESTING,
        "output_stage",
        create=True,
        new=None,
    ):
        coordinator = SignalStrategyTestingStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            strategy_factory=mock_factory,
            logger=mock_logger,
            strategy_combinators=[
                type("CombA", (), {"strategy_class": type("StrategyA", (), {})})
            ],
            optimization_root=".",
            optimization_json_filename="test.json",
        )
        coordinator.train_window_id = "20240101_20240131"
        coordinator.window_id = "20240201_2024-02-28"
        coordinator.train_start_date = datetime(2024, 1, 1)
        coordinator.train_end_date = datetime(2024, 1, 31)
        coordinator.test_start_date = datetime(2024, 2, 1)
        coordinator.test_end_date = datetime(2024, 2, 28)

        async def df_iter():
            yield pd.DataFrame({"a": [1]})

        prepared_data = {"AAPL": lambda: df_iter()}
        result = await coordinator._process_and_write(prepared_data)
        assert result == {}
        assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_process_warns_on_no_data(
    mock_loader,
    mock_manager,
    mock_executor,
    mock_evaluator,
    mock_factory,
    mock_logger,
    tmp_path,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    with mock.patch.object(
        BacktestStage.STRATEGY_TESTING,
        "output_stage",
        create=True,
        new=None,
    ):
        coordinator = SignalStrategyTestingStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            strategy_factory=mock_factory,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            optimization_root=".",
            optimization_json_filename="test.json",
        )
        coordinator.train_window_id = "20240101_20240131"
        coordinator.window_id = "20240201_20240228"
        coordinator.start_date = datetime(2024, 2, 1)
        coordinator.end_date = datetime(2024, 2, 28)

        async def empty_df_iter():
            if False:
                yield

        prepared_data = {"AAPL": lambda: empty_df_iter()}
        result = await coordinator._process_and_write(prepared_data)
        assert result == {}
        assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_write_is_noop(
    mock_loader,
    mock_manager,
    mock_executor,
    mock_evaluator,
    mock_factory,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    with mock.patch.object(
        BacktestStage.STRATEGY_TESTING,
        "output_stage",
        create=True,
        new=None,
    ):
        coordinator = SignalStrategyTestingStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            strategy_factory=mock_factory,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            optimization_root=".",
            optimization_json_filename="test.json",
        )
        coordinator.test_window_id = "test_window"
        coordinator.test_start_date = "2024-02-01"
        coordinator.test_end_date = "2024-02-28"

        result = coordinator._write_test_results(
            symbol="AAPL",
            strategy_name="StrategyA",
            metrics={"sharpe_ratio": 2.0},
            optimization_result={},
            collective_results={},
        )
        assert "AAPL" in result
        assert "StrategyA" in result["AAPL"]
        assert "test_window" in result["AAPL"]["StrategyA"]
        assert (
            result["AAPL"]["StrategyA"]["test_window"]["metrics"]["sharpe_ratio"] == 2.0
        )
