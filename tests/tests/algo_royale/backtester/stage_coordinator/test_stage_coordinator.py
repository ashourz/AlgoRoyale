from unittest.mock import ANY, AsyncMock, MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_stage_data_manager():
    mgr = MagicMock()
    mgr.write_error_file = MagicMock()
    return mgr


@pytest.fixture
def mock_data_loader():
    loader = MagicMock()
    loader.load_all_stage_data = AsyncMock(return_value={"AAPL": lambda: AsyncMock()})
    return loader


@pytest.fixture
def mock_data_preparer():
    preparer = MagicMock()
    preparer.normalized_stream = MagicMock(
        side_effect=lambda symbol, df_iter_factory, config: lambda: AsyncMock()
    )
    return preparer


@pytest.fixture
def mock_data_writer():
    writer = MagicMock()
    writer.save_stage_data = MagicMock()
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
        async def process(self, prepared_data):
            return prepared_data

    return TestCoordinator(
        stage=BacktestStage.DATA_INGEST,
        config={},
        data_loader=mock_data_loader,
        data_preparer=mock_data_preparer,
        data_writer=mock_data_writer,
        stage_data_manager=mock_stage_data_manager,
        logger=mock_logger,
    )


@pytest.mark.asyncio
async def test_run_success(coordinator, mock_data_loader, mock_data_writer):
    # Simulate a full successful run
    coordinator.input_stage = BacktestStage.DATA_INGEST
    coordinator.output_stage = BacktestStage.DATA_INGEST
    coordinator.stage.incoming_stage = BacktestStage.DATA_INGEST

    # Patch process to just return the prepared_data
    coordinator.process = AsyncMock(side_effect=lambda prepared_data: prepared_data)

    # Patch _write to not actually write
    coordinator._write = AsyncMock(return_value=True)

    result = await coordinator.run(strategy_name="strat")
    assert result is True
    mock_data_loader.load_all_stage_data.assert_called()
    coordinator._write.assert_called()


@pytest.mark.asyncio
async def test_run_no_incoming_stage(coordinator, mock_logger):
    coordinator.stage.incoming_stage = None
    result = await coordinator.run(strategy_name="strat")
    assert result is False
    # Check that the error log contains the expected substring
    assert any(
        "has no incoming stage defined" in str(call)
        for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_load_data_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage.incoming_stage = BacktestStage.DATA_INGEST
    mock_data_loader.load_all_stage_data = AsyncMock(return_value={})
    result = await coordinator.run(strategy_name="strat")
    assert result is False
    assert any(
        "No data loaded" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_prepare_data_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage.incoming_stage = BacktestStage.DATA_INGEST
    # Patch _prepare_data to return {}
    coordinator._prepare_data = MagicMock(return_value={})
    result = await coordinator.run(strategy_name="strat")
    assert result is False
    assert any(
        "No data prepared" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_run_process_failure(coordinator, mock_data_loader, mock_logger):
    coordinator.stage.incoming_stage = BacktestStage.DATA_INGEST
    # Patch process to return {}
    coordinator.process = AsyncMock(return_value={})
    result = await coordinator.run(strategy_name="strat")
    assert result is False
    assert any(
        "Processing failed" in str(call) for call in mock_logger.error.call_args_list
    )


@pytest.mark.asyncio
async def test_load_data_success(coordinator, mock_data_loader):
    coordinator.data_loader = mock_data_loader
    result = await coordinator._load_data(BacktestStage.DATA_INGEST)
    assert "AAPL" in result
    mock_data_loader.load_all_stage_data.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_exception(coordinator, mock_logger, mock_stage_data_manager):
    mock_loader = MagicMock()
    mock_loader.load_all_stage_data = AsyncMock(side_effect=Exception("fail"))
    coordinator.data_loader = mock_loader
    result = await coordinator._load_data(BacktestStage.DATA_INGEST)
    assert result == {}
    assert mock_logger.error.called
    assert mock_stage_data_manager.write_error_file.called


def test_prepare_data_success(coordinator):
    # Patch data_preparer.normalized_stream to return a dummy lambda
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
    # Patch data_preparer.normalized_stream to raise
    coordinator.data_preparer.normalized_stream = MagicMock(
        side_effect=Exception("fail")
    )
    data = {"AAPL": lambda: "df_iter"}
    result = coordinator._prepare_data(
        BacktestStage.DATA_INGEST, data, strategy_name="strat"
    )
    # Call the lambda to trigger the exception and error handling
    for symbol, factory in result.items():
        try:
            factory()
        except Exception:
            pass
    assert mock_logger.error.called
    assert mock_stage_data_manager.write_error_file.called


@pytest.mark.asyncio
async def test_write_success(coordinator, mock_data_writer):
    # Prepare a processed_data dict with an async generator
    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    processed_data = {"AAPL": lambda: async_gen()}
    await coordinator._write(
        BacktestStage.DATA_INGEST, processed_data, strategy_name="strat"
    )
    mock_data_writer.save_stage_data.assert_called_with(
        stage=BacktestStage.DATA_INGEST,
        strategy_name="strat",
        symbol="AAPL",
        results_df=ANY,
    )


@pytest.mark.asyncio
async def test_write_exception(coordinator, mock_logger, mock_stage_data_manager):
    # Patch save_stage_data to raise
    async def async_gen():
        yield pd.DataFrame({"a": [1]})

    processed_data = {"AAPL": lambda: async_gen()}
    coordinator.data_writer.save_stage_data = MagicMock(side_effect=Exception("fail"))
    await coordinator._write(
        BacktestStage.DATA_INGEST, processed_data, strategy_name="strat"
    )
    assert mock_logger.error.called
    assert mock_stage_data_manager.write_error_file.called
