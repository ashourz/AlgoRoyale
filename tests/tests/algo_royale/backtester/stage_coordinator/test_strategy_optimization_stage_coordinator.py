from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

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
def mock_factory():
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


@pytest.mark.asyncio
async def test_init_success(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_factory,
    mock_executor,
    mock_evaluator,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_factory,
    mock_executor,
    mock_evaluator,
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

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with (
        patch(
            "algo_royale.strategy_factory.optimizer.strategy_optimizer.StrategyOptimizer",
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
    mock_factory,
    mock_executor,
    mock_evaluator,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with (
        patch(
            "algo_royale.strategy_factory.optimizer.strategy_optimizer.StrategyOptimizer",
        ) as MockOptimizer,
        patch.object(
            coordinator,
            "_backtest_and_evaluate",
            new=AsyncMock(side_effect=Exception("Test error")),
        ),
        patch("builtins.open", create=True),
        patch("json.load", return_value={}),
    ):
        instance = MockOptimizer.return_value
        instance.optimize.side_effect = Exception("Test error")
        result = await coordinator.process(prepared_data)
        assert result == {}


@pytest.mark.asyncio
async def test_process_skips_symbol_with_no_data(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_factory,
    mock_executor,
    mock_evaluator,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
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
            "algo_royale.strategy_factory.optimizer.strategy_optimizer.StrategyOptimizer",
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
    mock_factory,
    mock_executor,
    mock_evaluator,
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

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[CombA, CombB],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with (
        patch(
            "algo_royale.strategy_factory.optimizer.strategy_optimizer.StrategyOptimizer",
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
    mock_factory,
    mock_executor,
    mock_evaluator,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with (
        patch(
            "algo_royale.strategy_factory.optimizer.strategy_optimizer.StrategyOptimizer",
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
    mock_factory,
    mock_executor,
    mock_evaluator,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

        @staticmethod
        def get_condition_types():
            return {"entry": [], "exit": []}

    coordinator = StrategyOptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
    )
    result = await coordinator._write(None, None)
    assert result is None
