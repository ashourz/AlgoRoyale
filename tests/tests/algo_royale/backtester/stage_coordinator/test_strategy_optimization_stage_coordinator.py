from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    mockSignalStrategyOptimizerFactory,
)
from algo_royale.backtester.stage_coordinator.optimization.signal_strategy_optimization_stage_coordinator import (
    SignalStrategyOptimizationStageCoordinator,
)
from algo_royale.logging.logger_factory import mockLogger


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
def mock_manager():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return mockLogger()


@pytest.fixture
def mock_executor():
    exec = MagicMock()
    exec.run_backtest = AsyncMock(
        return_value={"AAPL": [pd.DataFrame({"result": [1]})]}
    )
    return exec


@pytest.fixture
def mock_evaluator():
    eval = MagicMock()
    eval.evaluate.return_value = {"sharpe": 2.0}
    return eval


@pytest.fixture
def mock_signal_strategy_optimizer_factory():
    factory = mockSignalStrategyOptimizerFactory()
    factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    return factory


@pytest.mark.asyncio
async def test_init_success(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        __name__ = "DummyStrategy"

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    # Patch output_stage on BacktestStage.STRATEGY_OPTIMIZATION for test robustness
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class StratA:
        pass

    class StratB:
        pass

    class DummyStrategy:
        __name__ = "DummyStrategy"

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        coordinator.start_date = datetime(2024, 1, 1)
        coordinator.end_date = datetime(2024, 1, 31)
        coordinator.window_id = "20240101_20240131"

        async def df_iter():
            yield pd.DataFrame({"a": [1]})

        prepared_data = {"AAPL": lambda: df_iter()}

        with (
            patch(
                "algo_royale.backtester.optimizer.signal.signal_strategy_optimizer.SignalStrategyOptimizerImpl",
                autospec=True,
            ) as MockOptimizer,
            patch.object(
                coordinator,
                "_backtest_and_evaluate",
                new=AsyncMock(return_value={"score": 0.95}),
            ),
            patch("builtins.open", create=True),
            patch("json.load", return_value={}),
        ):
            mock_optimizer_instance = MagicMock()
            mock_optimizer_instance.setOptimizeResults(
                {
                    "strategy": "DummyStrategy",
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
                }
            )
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator._process_and_write(prepared_data)
            mock_logger.debug(f"Test result: {result}")
            assert "AAPL" in result
            assert "DummyStrategy" in result["AAPL"]
            # The result should be a dict with window_id as a key for the DummyStrategy
            assert coordinator.window_id in result["AAPL"]["DummyStrategy"]
            # The value should be the optimization result
            strategy_result = result["AAPL"]["DummyStrategy"][coordinator.window_id]
            assert strategy_result["optimization"]["strategy"] == "DummyStrategy"
            assert "best_value" in strategy_result["optimization"]
            assert "best_params" in strategy_result["optimization"]
            assert "meta" in strategy_result["optimization"]
            assert "metrics" in strategy_result["optimization"]


@pytest.mark.asyncio
async def test_fetch_symbol_optimization_exception_logs_error(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        __name__ = "DummyStrategy"

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        coordinator.start_date = datetime(2024, 1, 1)
        coordinator.end_date = datetime(2024, 1, 31)
        coordinator.window_id = "20240101_20240131"

        async def df_iter():
            yield pd.DataFrame({"a": [1]})

        prepared_data = {"AAPL": lambda: df_iter()}

        # Simulate optimizer exception by swapping the factory's create method for this test
        class FailingOptimizer:
            def optimize(self, *a, **k):
                raise Exception("Test error")

        optimizer_factory.create = lambda *a, **k: FailingOptimizer()

        result = await coordinator._process_and_write(prepared_data)
        assert result == {}


@pytest.mark.asyncio
async def test_process_skips_symbol_with_no_data(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        __name__ = "DummyStrategy"

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        coordinator.start_date = datetime(2024, 1, 1)
        coordinator.end_date = datetime(2024, 1, 31)
        coordinator.window_id = "20240101_20240131"

        async def empty_df_iter():
            if False:
                yield

        prepared_data = {"AAPL": lambda: empty_df_iter()}

        with (
            patch(
                "algo_royale.backtester.optimizer.signal.signal_strategy_optimizer.SignalStrategyOptimizerImpl",
                autospec=True,
            ) as MockOptimizer,
            patch.object(
                coordinator,
                "_backtest_and_evaluate",
                new=AsyncMock(return_value={"score": 0.95}),
            ),
            patch("builtins.open", create=True),
            patch("json.load", return_value={}),
        ):
            mock_optimizer_instance = MagicMock()
            mock_optimizer_instance.setOptimizeResults(
                {
                    "strategy": "DummyStrategy",
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
                }
            )
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator._process_and_write(prepared_data)
            assert result == {}


@pytest.mark.asyncio
async def test_process_multiple_strategies(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class StratA:
        pass

    class StratB:
        pass

    class CombA:
        strategy_class = StratA

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    class CombB:
        strategy_class = StratB

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[CombA, CombB],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        coordinator.start_date = datetime(2024, 1, 1)
        coordinator.end_date = datetime(2024, 1, 31)
        coordinator.window_id = "20240101_20240131"

        async def df_iter():
            yield pd.DataFrame({"a": [1]})

        prepared_data = {"AAPL": lambda: df_iter()}

        with (
            patch(
                "algo_royale.backtester.optimizer.signal.signal_strategy_optimizer.SignalStrategyOptimizerImpl",
                autospec=True,
            ) as MockOptimizer,
            patch.object(
                coordinator,
                "_backtest_and_evaluate",
                new=AsyncMock(return_value={"score": 0.95}),
            ),
            patch("builtins.open", create=True),
            patch("json.load", return_value={}),
        ):
            mock_optimizer_instance = MagicMock()
            mock_optimizer_instance.setOptimizeResults(
                {
                    "strategy": "DummyStrategy",
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
                }
            )
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator._process_and_write(prepared_data)
            assert "AAPL" in result
            assert "StratA" in result["AAPL"]
            assert "StratB" in result["AAPL"]


@pytest.mark.asyncio
async def test_process_optimizer_exception_logs_error(
    mock_loader,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,  # <-- add fixture
):
    class DummyStrategy:
        __name__ = "DummyStrategy"

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "20240101_20240131": {
                "optimization": {
                    "strategy": "DummyStrategy",
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
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = SignalStrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        coordinator.start_date = datetime(2024, 1, 1)
        coordinator.end_date = datetime(2024, 1, 31)
        coordinator.window_id = "20240101_20240131"

        async def df_iter():
            yield pd.DataFrame({"a": [1]})

        prepared_data = {"AAPL": lambda: df_iter()}

        with (
            patch(
                "algo_royale.backtester.optimizer.signal.signal_strategy_optimizer.SignalStrategyOptimizerImpl",
            ) as MockOptimizer,
            patch.object(
                coordinator,
                "_backtest_and_evaluate",
                new=AsyncMock(return_value={"score": 0.95}),
            ),
            patch("builtins.open", create=True),
            patch("json.load", return_value={}),
        ):
            instance = MockOptimizer.return_value
            instance.optimize.side_effect = Exception("Test error")
            result = await coordinator._process_and_write(prepared_data)
            assert "AAPL" in result
            assert "DummyStrategy" in result["AAPL"]
            assert coordinator.window_id in result["AAPL"]["DummyStrategy"]
