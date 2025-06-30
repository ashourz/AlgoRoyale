from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    mockSignalStrategyOptimizerFactory,
)
from algo_royale.backtester.stage_coordinator.optimization.strategy_optimization_stage_coordinator import (
    StrategyOptimizationStageCoordinator,
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
def mock_manager():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return MagicMock()


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
    return mockSignalStrategyOptimizerFactory()


@pytest.mark.asyncio
async def test_init_success(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    # Patch output_stage on BacktestStage.STRATEGY_OPTIMIZATION for test robustness
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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
    mock_preparer,
    mock_writer,
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
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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
            mock_optimizer_instance.optimize.return_value = {"param": 1, "score": 0.95}
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator.process(prepared_data)
            assert "AAPL" in result
            assert "DummyStrategy" in result["AAPL"]
            # The result should be a dict with window_id as a key for the DummyStrategy
            assert coordinator.window_id in result["AAPL"]["DummyStrategy"]
            # The value should be the optimization result
            result = await coordinator.process(prepared_data)
            strategy_result = result["AAPL"]["DummyStrategy"][coordinator.window_id]

            assert strategy_result["strategy"] == "DummyStrategy"
            assert "best_value" in strategy_result
            assert "best_params" in strategy_result
            assert "meta" in strategy_result
            assert "metrics" in strategy_result


@pytest.mark.asyncio
async def test_fetch_symbol_optimization_exception_logs_error(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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

        result = await coordinator.process(prepared_data)
        assert result == {}


@pytest.mark.asyncio
async def test_process_skips_symbol_with_no_data(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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
            mock_optimizer_instance.optimize.return_value = {"param": 1, "score": 0.95}
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator.process(prepared_data)
            assert result == {}


@pytest.mark.asyncio
async def test_process_multiple_strategies(
    mock_loader,
    mock_preparer,
    mock_writer,
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
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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
            mock_optimizer_instance.optimize.return_value = {"param": 1, "score": 0.95}
            MockOptimizer.return_value = mock_optimizer_instance
            result = await coordinator.process(prepared_data)
            assert "AAPL" in result
            assert "StratA" in result["AAPL"]
            assert "StratB" in result["AAPL"]


@pytest.mark.asyncio
async def test_process_optimizer_exception_logs_error(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,  # <-- add fixture
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
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
            result = await coordinator.process(prepared_data)
            assert "AAPL" in result
            assert "DummyStrategy" in result["AAPL"]
            assert coordinator.window_id in result["AAPL"]["DummyStrategy"]


@pytest.mark.asyncio
async def test_write_is_noop(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_executor,
    mock_evaluator,
    mock_signal_strategy_optimizer_factory,  # <-- add fixture
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    optimizer_factory = mock_signal_strategy_optimizer_factory
    optimizer_factory.setCreatedOptimizerResult(
        {
            "strategy": "DummyStrategy",
            "best_params": {"param1": 1, "param2": 2},
            "best_value": 0.95,
            "meta": {"symbol": "AAPL", "window_id": "20240101_20240131"},
            "metrics": {"sharpe": 2.0},
        }
    )
    with patch.object(
        BacktestStage.STRATEGY_OPTIMIZATION, "output_stage", create=True, new=None
    ):
        coordinator = StrategyOptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=[DummyCombinator],
            strategy_executor=mock_executor,
            strategy_evaluator=mock_evaluator,
            optimization_root=".",
            optimization_json_filename="test.json",
            signal_strategy_optimizer_factory=optimizer_factory,
        )
        result = await coordinator._write(None, None)
        assert result is None
