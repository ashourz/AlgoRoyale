from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.optimization_stage_coordinator import (
    OptimizationStageCoordinator,
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


def test_init_success(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )


def test_init_no_combinators(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    with pytest.raises(ValueError):
        OptimizationStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            strategy_combinators=None,
        )


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"

    # Mock optimizer and strategy_factory
    coordinator.optimizer = MagicMock()
    coordinator.strategy_factory = MagicMock()
    coordinator.strategy_factory.get_strategy_class.return_value = DummyStrategy
    coordinator.optimizer.optimize.return_value = {"param": 1, "score": 0.95}

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    # Patch open to avoid actual file I/O and JSONDecodeError
    with patch("builtins.open", create=True), patch("json.load", return_value={}):
        result = await coordinator.process(prepared_data)
    assert "AAPL" in result
    assert "DummyStrategy" in result["AAPL"]
    assert coordinator.window_id in result["AAPL"]["DummyStrategy"]


@pytest.mark.asyncio
async def test_fetch_symbol_optimization_exception_logs_error(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    with pytest.raises(Exception):
        async for df in coordinator._fetch_symbol_optimization("AAPL"):
            results.append(df)


@pytest.mark.asyncio
async def test_process_skips_symbol_with_no_data(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"
    coordinator.optimizer = MagicMock()
    coordinator.strategy_factory = MagicMock()
    coordinator.strategy_factory.get_strategy_class.return_value = DummyStrategy
    coordinator.optimizer.optimize.return_value = {"param": 1, "score": 0.95}

    async def empty_df_iter():
        if False:
            yield

    prepared_data = {"AAPL": lambda: empty_df_iter()}

    with patch("builtins.open", create=True), patch("json.load", return_value={}):
        result = await coordinator.process(prepared_data)
    assert result == {}
    assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_process_multiple_strategies(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class StratA:
        pass

    class StratB:
        pass

    class CombA:
        strategy_class = StratA

    class CombB:
        strategy_class = StratB

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[CombA, CombB],
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"
    coordinator.optimizer = MagicMock()
    coordinator.strategy_factory = MagicMock()
    coordinator.strategy_factory.get_strategy_class.side_effect = [StratA, StratB]
    coordinator.optimizer.optimize.return_value = {"param": 1, "score": 0.95}

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with patch("builtins.open", create=True), patch("json.load", return_value={}):
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
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    coordinator.window_id = "20240101_20240131"
    coordinator.optimizer = MagicMock()
    coordinator.strategy_factory = MagicMock()
    coordinator.strategy_factory.get_strategy_class.return_value = DummyStrategy
    coordinator.optimizer.optimize.side_effect = Exception("fail!")

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    prepared_data = {"AAPL": lambda: df_iter()}

    with patch("builtins.open", create=True), patch("json.load", return_value={}):
        result = await coordinator.process(prepared_data)
    assert result == {}
    assert mock_logger.error.called


@pytest.mark.asyncio
async def test_write_is_noop(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
):
    class DummyStrategy:
        pass

    class DummyCombinator:
        strategy_class = DummyStrategy

    coordinator = OptimizationStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        strategy_combinators=[DummyCombinator],
    )
    result = await coordinator._write(None, None)
    assert result is None
