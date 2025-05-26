from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.mock_stage_coordinator import (
    MockStageCoordinator,
)


@pytest.fixture
def mock_dependencies():
    return {
        "stage": MagicMock(spec=BacktestStage),
        "config": {},
        "data_loader": MagicMock(),
        "data_preparer": MagicMock(),
        "data_writer": MagicMock(),
        "pipeline_data_manager": MagicMock(),
        "logger": MagicMock(),
    }


@pytest.mark.asyncio
async def test_run_success(mock_dependencies):
    # Arrange
    coordinator = MockStageCoordinator(**mock_dependencies)  # noqa: F821
    coordinator.stage.incoming_stage = MagicMock()
    coordinator.data_loader.load_all_stage_data = AsyncMock(
        return_value={
            "AAPL": lambda: AsyncMock(return_value=[pd.DataFrame({"a": [1]})])
        }
    )
    coordinator.data_preparer.normalized_stream = MagicMock(
        return_value=lambda: AsyncMock(return_value=[pd.DataFrame({"a": [1]})])
    )
    coordinator.process_return = {
        "AAPL": lambda: AsyncMock(return_value=[pd.DataFrame({"a": [1]})])
    }
    coordinator.data_writer.save_stage_data = MagicMock()

    # Act
    result = await coordinator.run(strategy_name="test_strategy")

    # Assert
    assert result is True
    assert coordinator.process_called
    coordinator.data_writer.save_stage_data.assert_called()


@pytest.mark.asyncio
async def test_run_no_incoming_stage(mock_dependencies):
    coordinator = MockStageCoordinator(**mock_dependencies)
    coordinator.stage.incoming_stage = None
    coordinator.process_return = {
        "AAPL": lambda: AsyncMock(return_value=[pd.DataFrame({"a": [1]})])
    }
    coordinator.data_writer.save_stage_data = MagicMock()

    result = await coordinator.run(strategy_name="test_strategy")
    assert result is True
    assert coordinator.process_called


@pytest.mark.asyncio
async def test_run_load_data_failure(mock_dependencies):
    coordinator = MockStageCoordinator(**mock_dependencies)
    coordinator.stage.incoming_stage = MagicMock()
    coordinator.data_loader.load_all_stage_data = AsyncMock(
        side_effect=Exception("fail")
    )
    result = await coordinator.run(strategy_name="test_strategy")
    assert result is False


@pytest.mark.asyncio
async def test_run_prepare_data_failure(mock_dependencies):
    coordinator = MockStageCoordinator(**mock_dependencies)
    coordinator.stage.incoming_stage = MagicMock()
    coordinator.data_loader.load_all_stage_data = AsyncMock(
        return_value={"AAPL": lambda: AsyncMock()}
    )
    # Patch _prepare_data to fail
    with patch.object(coordinator, "_prepare_data", return_value={}):
        result = await coordinator.run(strategy_name="test_strategy")
        assert result is False


@pytest.mark.asyncio
async def test_run_process_failure(mock_dependencies):
    coordinator = MockStageCoordinator(**mock_dependencies)
    coordinator.stage.incoming_stage = MagicMock()
    coordinator.data_loader.load_all_stage_data = AsyncMock(
        return_value={"AAPL": lambda: AsyncMock()}
    )
    coordinator.data_preparer.normalized_stream = MagicMock(
        return_value=lambda: AsyncMock()
    )
    coordinator.process_return = {}
    result = await coordinator.run(strategy_name="test_strategy")
    assert result is False
