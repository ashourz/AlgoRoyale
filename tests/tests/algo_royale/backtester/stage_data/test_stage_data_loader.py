from unittest.mock import AsyncMock, MagicMock

import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage


@pytest.fixture
def mock_config():
    """Fixture for a mock config that always returns a valid watchlist path."""
    config = MagicMock()
    config.get.return_value = "mock_watchlist_path"
    return config


@pytest.fixture
def mock_logger():
    """Fixture for a mock logger."""
    return MagicMock()


@pytest.fixture
def mock_stage_data_manager():
    """Fixture for a mock stage data manager."""
    mgr = MagicMock()
    mgr.get_directory_path.return_value.exists.return_value = True
    return mgr


def test_init_success(mock_config, mock_logger, mock_stage_data_manager):
    """Test successful initialization with a non-empty watchlist."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    loader = StageDataLoader(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist_path",
    )
    assert loader.get_watchlist() == ["AAPL", "GOOG"]
    mock_logger.info.assert_called_with("BacktestDataLoader initialized")


def test_init_missing_watchlist_path(mock_logger, mock_stage_data_manager):
    """Test initialization fails with missing watchlist path."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    with pytest.raises(RuntimeError) as excinfo:
        StageDataLoader(
            logger=mock_logger,
            stage_data_manager=mock_stage_data_manager,
            load_watchlist=lambda path: ["AAPL", "GOOG"],
            watchlist_path_string="",  # <-- pass empty string here!
        )
    assert "Watchlist path not specified in config" in str(excinfo.value)


def test_init_empty_watchlist(mock_config, mock_logger, mock_stage_data_manager):
    """Test initialization fails with an empty watchlist."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    with pytest.raises(RuntimeError) as excinfo:
        StageDataLoader(
            logger=mock_logger,
            stage_data_manager=mock_stage_data_manager,
            load_watchlist=lambda path: [],
            watchlist_path_string="mock_watchlist_path",
        )
    assert "Watchlist is empty" in str(excinfo.value)


@pytest.mark.asyncio
async def test_load_all_stage_data(mock_config, mock_logger, mock_stage_data_manager):
    """Test async loading of all stage data returns correct generators."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    loader = StageDataLoader(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist_path",
    )
    loader._ensure_all_data_exists = AsyncMock()
    loader.load_symbol = AsyncMock()

    # Mock _get_all_existing_data_symbols to return the expected symbols
    loader._get_all_existing_data_symbols = AsyncMock(return_value=["AAPL", "GOOG"])

    result = await loader.load_all_stage_data(BacktestStage.DATA_INGEST)
    assert "AAPL" in result and "GOOG" in result
    assert callable(result["AAPL"])
    assert callable(result["GOOG"])


@pytest.mark.asyncio
async def test_load_symbol_no_data(mock_config, mock_logger, mock_stage_data_manager):
    """Test async symbol loading raises ValueError if no data exists."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    loader = StageDataLoader(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist_path",
    )
    loader._get_stage_symbol_dir = MagicMock(return_value=MagicMock())
    loader._has_existing_data = MagicMock(return_value=False)  # <-- Use MagicMock here

    with pytest.raises(ValueError):
        async for _ in loader.load_symbol(BacktestStage.DATA_INGEST, "AAPL"):
            pass


@pytest.mark.asyncio
async def test_load_symbol_with_data(mock_config, mock_logger, mock_stage_data_manager):
    """Test async symbol loading yields dataframes if data exists."""
    from algo_royale.backtester.stage_data.loader.stage_data_loader import (
        StageDataLoader,
    )

    loader = StageDataLoader(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist_path",
    )
    loader._get_stage_symbol_dir = MagicMock(return_value=MagicMock())
    loader._has_existing_data = AsyncMock(return_value=True)

    async def async_gen():
        yield MagicMock()

    loader._stream_existing_data_async = lambda **kwargs: async_gen()

    result = []
    async for df in loader.load_symbol(BacktestStage.DATA_INGEST, "AAPL"):
        result.append(df)
    assert result  # Should yield at least one DataFrame
