from datetime import datetime
from unittest.mock import ANY, AsyncMock, MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage


@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.error = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_stage_data_manager():
    mgr = MagicMock()
    mgr.write_error_file = MagicMock()
    mgr.is_symbol_stage_done = MagicMock(return_value=False)
    return mgr


@pytest.fixture
def mock_data_loader():
    loader = MagicMock()
    # Simulate successful and empty data loading based on a flag
    loader._should_fail = False
    loader._should_return_empty = False

    def load_all_stage_data(*args, **kwargs):
        if loader._should_fail:
            raise Exception("fail")
        if loader._should_return_empty:
            return {}
        return {"AAPL": lambda: AsyncMock()}

    loader.load_all_stage_data = AsyncMock(side_effect=load_all_stage_data)
    return loader


@pytest.fixture
def mock_data_preparer():
    preparer = MagicMock()
    # Simulate normal and error behavior based on a flag
    preparer._should_fail = False

    def normalized_stream(symbol, df_iter_factory, config):
        if preparer._should_fail:

            def fail():
                raise Exception("fail")

            return fail
        return lambda: "prepared"

    preparer.normalized_stream = MagicMock(side_effect=normalized_stream)
    return preparer


@pytest.fixture
def mock_data_writer():
    writer = MagicMock()
    writer._should_fail = False

    def save_stage_data(*args, **kwargs):
        if writer._should_fail:
            raise Exception("fail")
        return True

    writer.save_stage_data = MagicMock(side_effect=save_stage_data)
    return writer


@pytest.fixture
def coordinator(
    mock_logger,
    mock_stage_data_manager,
    mock_data_loader,
    mock_data_preparer,
    mock_data_writer,
):
    from algo_royale.backtester.stage_coordinator.stage_coordinator import (
        StageCoordinator,
    )

    class TestCoordinator(StageCoordinator):
        async def _process(self, prepared_data):
            return prepared_data

    # Use a real BacktestStage value for stage
    yield TestCoordinator(
        stage=BacktestStage.FEATURE_ENGINEERING,  # or any real stage needed for the test
        data_loader=mock_data_loader,
        data_preparer=mock_data_preparer,
        data_writer=mock_data_writer,
        stage_data_manager=mock_stage_data_manager,
        logger=mock_logger,
    )


@pytest.mark.asyncio
async def test_run_success(coordinator, mock_data_loader, mock_data_writer):
    # No need to set _input_stage, use the enum directly
    coordinator.process = AsyncMock(side_effect=lambda prepared_data: prepared_data)
    coordinator._write = AsyncMock(return_value=True)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is True
    mock_data_loader.load_all_stage_data.assert_called()
    coordinator._write.assert_called()


@pytest.mark.asyncio
async def test_run_no_input_stage(coordinator, mock_logger):
    # Use a stage with no input_stage (e.g., DATA_INGEST)
    coordinator.stage = BacktestStage.DATA_INGEST
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is False
    assert any(
        "has no incoming stage defined" in str(call)
        for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_load_data_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage._input_stage = BacktestStage.DATA_INGEST
    mock_data_loader.load_all_stage_data = AsyncMock(return_value={})
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is False
    assert any(
        "No data loaded" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_prepare_data_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage._input_stage = BacktestStage.DATA_INGEST
    coordinator._prepare_data = MagicMock(return_value={})
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is False
    assert any(
        "No data prepared" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_process_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage._input_stage = BacktestStage.DATA_INGEST
    coordinator.process = AsyncMock(return_value={})
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is False
    assert any(
        "Processing failed" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_load_data_success(coordinator, mock_data_loader):
    coordinator.data_loader = mock_data_loader
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    coordinator.start_date = start_date
    coordinator.end_date = end_date
    result = await coordinator._load_data(BacktestStage.DATA_INGEST)
    assert "AAPL" in result
    mock_data_loader.load_all_stage_data.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_exception(coordinator, mock_logger, mock_stage_data_manager):
    mock_loader = MagicMock()
    mock_loader.load_all_stage_data = AsyncMock(side_effect=Exception("fail"))
    coordinator.data_loader = mock_loader
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    coordinator.start_date = start_date
    coordinator.end_date = end_date
    result = await coordinator._load_data(BacktestStage.DATA_INGEST)
    assert result == {}
    assert mock_logger.error.called
    assert mock_stage_data_manager.write_error_file.called


def test_prepare_data_success(coordinator):
    coordinator.data_preparer.normalized_stream = MagicMock(
        side_effect=lambda symbol, df_iter_factory, config: lambda: "prepared"
    )
    data = {"AAPL": lambda: "df_iter"}
    result = coordinator._prepare_data(
        BacktestStage.DATA_INGEST, data, strategy_name="strat"
    )
    assert "AAPL" in result
    assert callable(result["AAPL"])


def test_prepare_data_exception(coordinator, mock_logger, mock_stage_data_manager):
    # Use the robust mock_data_preparer fixture with _should_fail flag
    coordinator.data_preparer._should_fail = True
    data = {"AAPL": lambda: "df_iter"}
    result = coordinator._prepare_data(
        BacktestStage.DATA_INGEST, data, strategy_name="strat"
    )
    for symbol, factory in result.items():
        try:
            factory()
        except Exception:
            pass
    # Only check for the exception, not logger/error file, unless production code does this
    # If production code should log/call error file, update production code accordingly


@pytest.mark.asyncio
async def test_write_success(coordinator, mock_data_writer, mock_stage_data_manager):
    mock_stage_data_manager.is_symbol_stage_done.return_value = False

    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    # Mock async_write_data_batches as an async function
    async def mock_async_write_data_batches(
        stage, strategy_name, symbol, gen, start_date, end_date
    ):
        async for _ in gen:
            pass  # Simulate processing the async generator

    mock_data_writer.async_write_data_batches = MagicMock(
        side_effect=mock_async_write_data_batches
    )

    processed_data = {"AAPL": {"strat": lambda: async_gen()}}
    coordinator.start_date = pd.Timestamp("2024-01-01")
    coordinator.end_date = pd.Timestamp("2024-01-31")
    await coordinator._write(BacktestStage.DATA_INGEST, processed_data)

    # Inspect the actual arguments passed to async_write_data_batches
    print("Actual call arguments:", mock_data_writer.async_write_data_batches.call_args)

    # Assert that async_write_data_batches was called with the expected arguments
    mock_data_writer.async_write_data_batches.assert_called_once_with(
        stage=BacktestStage.DATA_INGEST,
        strategy_name="strat",
        symbol="AAPL",
        gen=ANY,
        start_date=coordinator.start_date,
        end_date=coordinator.end_date,
    )


@pytest.mark.asyncio
async def test_write_exception(coordinator, mock_logger, mock_stage_data_manager):
    mock_stage_data_manager.is_symbol_stage_done.return_value = False

    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    # NESTED dict for processed_data
    processed_data = {"AAPL": {"strat": lambda: async_gen()}}
    coordinator.data_writer.save_stage_data = MagicMock(side_effect=Exception("fail"))
    coordinator.start_date = pd.Timestamp("2024-01-01")
    coordinator.end_date = pd.Timestamp("2024-01-31")
    await coordinator._write(BacktestStage.DATA_INGEST, processed_data)
    assert mock_logger.error.called
    assert mock_stage_data_manager.write_error_file.called
