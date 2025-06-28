from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.testing.strategy_testing_stage_coordinator import (
    StrategyTestingStageCoordinator,
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
        lambda stage, strategy_name, symbol: tmp_path
        / f"{stage}_{strategy_name}_{symbol}"
    )
    return mgr


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
def mock_factory():
    fac = MagicMock()
    fac.build_strategy.return_value = MagicMock()
    return fac


def test_init_success(
    mock_loader,
    mock_preparer,
    mock_writer,
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

    StrategyTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        optimization_root=".",
        optimization_json_filename="test.json",
    )


@pytest.mark.asyncio
async def test_process_returns_metrics(
    mock_loader,
    mock_preparer,
    mock_writer,
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

    # Prepare a fake optimization_result.json with best_params
    opt_dir = tmp_path / "optimization_StrategyA_AAPL"
    opt_dir.mkdir(parents=True, exist_ok=True)
    opt_path = (
        opt_dir / "test.json"
    )  # <-- changed from optimization_result.json to test.json
    train_window_id = "20240101_20240131"
    test_window_id = "20240201_20240228"
    with open(opt_path, "w") as f:
        import json

        json.dump(
            {train_window_id: {"optimization": {"best_params": {"foo": "bar"}}}}, f
        )

    # Patch get_directory_path to point to our temp dir
    mock_manager.get_directory_path.side_effect = (
        lambda stage, strategy_name, symbol, *args, **kwargs: tmp_path
        / f"optimization_{strategy_name}_{symbol}"
    )
    mock_manager.get_extended_path.side_effect = (
        lambda base_dir, strategy_name, symbol, start_date, end_date: tmp_path
        / f"optimization_{strategy_name}_{symbol}"
    )
    StrategyA = type("StrategyA", (), {})
    CombA = type("CombA", (), {"strategy_class": StrategyA})
    coordinator = StrategyTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[CombA],
        optimization_root=".",
        optimization_json_filename="test.json",
    )
    coordinator.train_window_id = train_window_id
    coordinator.test_window_id = test_window_id  # <-- add this line
    coordinator.train_start_date = datetime(2024, 1, 1)
    coordinator.train_end_date = datetime(2024, 1, 31)
    coordinator.test_start_date = datetime(2024, 2, 1)
    coordinator.test_end_date = datetime(2024, 2, 28)

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}
    mock_factory.build_strategy.return_value = StrategyA()
    result = await coordinator.process(prepared_data)
    assert "AAPL" in result
    assert "StrategyA" in result["AAPL"]
    assert test_window_id in result["AAPL"]["StrategyA"]
    assert result["AAPL"]["StrategyA"][test_window_id]["sharpe"] == 2.0


@pytest.mark.asyncio
async def test_process_warns_on_missing_optimization(
    mock_loader,
    mock_preparer,
    mock_writer,
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

    # Patch get_directory_path to point to a non-existent file
    mock_manager.get_directory_path.side_effect = (
        lambda stage, strategy_name, symbol, *args, **kwargs: tmp_path
        / f"optimization_{strategy_name}_{symbol}"
    )

    coordinator = StrategyTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
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

    result = await coordinator.process(prepared_data)
    assert result == {}
    assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_process_warns_on_no_data(
    mock_loader,
    mock_preparer,
    mock_writer,
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

    # Patch get_directory_path to point to a real temp dir
    mock_manager.get_directory_path.side_effect = (
        lambda stage, strategy_name, symbol: tmp_path
        / f"optimization_{strategy_name}_{symbol}"
    )

    coordinator = StrategyTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
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

    result = await coordinator.process(prepared_data)
    assert result == {}
    assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_write_is_noop(
    mock_loader,
    mock_preparer,
    mock_writer,
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

    coordinator = StrategyTestingStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        strategy_executor=mock_executor,
        strategy_evaluator=mock_evaluator,
        strategy_factory=mock_factory,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
        optimization_root=".",
        optimization_json_filename="test.json",
    )
    result = await coordinator._write(None, None)
    assert result is None
