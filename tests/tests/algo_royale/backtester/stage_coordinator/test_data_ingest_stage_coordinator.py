from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.get.side_effect = lambda section, key=None: {
        ("paths.backtester", "watchlist_path"): "mock_watchlist.txt",
        ("backtest", "start_date"): "2024-01-01",
        ("backtest", "end_date"): "2024-01-31",
    }[(section, key)]
    return config


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
def mock_quote_service():
    service = MagicMock()
    service.fetch_historical_bars = AsyncMock()
    service.client.aclose = AsyncMock()
    return service


def test_init_success(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    from algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator import (
        DataIngestStageCoordinator,
    )

    # Should not raise
    DataIngestStageCoordinator(
        config=mock_config,
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
    )


def test_init_missing_dates(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    mock_config.get.side_effect = lambda section, key=None: {
        ("paths.backtester", "watchlist_path"): "mock_watchlist.txt",
        ("backtest", "start_date"): None,
        ("backtest", "end_date"): None,
    }[(section, key)]
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            config=mock_config,
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: ["AAPL"],
        )


def test_init_missing_watchlist_path(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    mock_config.get.side_effect = lambda section, key=None: {
        ("paths.backtester", "watchlist_path"): "",
        ("backtest", "start_date"): "2024-01-01",
        ("backtest", "end_date"): "2024-01-31",
    }[(section, key)]
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            config=mock_config,
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: ["AAPL"],
        )


def test_init_empty_watchlist(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            config=mock_config,
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: [],
        )


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    coordinator = DataIngestStageCoordinator(
        config=mock_config,
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
    )
    result = await coordinator.process()
    assert "AAPL" in result and "GOOG" in result
    assert callable(result["AAPL"][None])
    assert callable(result["GOOG"][None])


@pytest.mark.asyncio
async def test_fetch_symbol_data_success(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    # Mock a response with two pages
    class DummyBar:
        def model_dump(self):
            return {"open": 1, "close": 2}

    class DummyResponse:
        def __init__(self, bars, next_page_token=None):
            self.symbol_bars = {"AAPL": bars}
            self.next_page_token = next_page_token

    mock_quote_service.fetch_historical_bars.side_effect = [
        DummyResponse([DummyBar(), DummyBar()], next_page_token="token2"),
        DummyResponse([DummyBar()], next_page_token=None),
    ]
    coordinator = DataIngestStageCoordinator(
        config=mock_config,
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
    )
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert len(results) == 2
    assert all(isinstance(df, pd.DataFrame) for df in results)
    assert mock_quote_service.fetch_historical_bars.await_count == 2
    assert mock_quote_service.client.aclose.await_count == 1


@pytest.mark.asyncio
async def test_fetch_symbol_data_no_data_warns(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    class DummyResponse:
        def __init__(self):
            self.symbol_bars = {"AAPL": []}
            self.next_page_token = None

    mock_quote_service.fetch_historical_bars.return_value = DummyResponse()
    coordinator = DataIngestStageCoordinator(
        config=mock_config,
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
    )
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert results == []
    mock_logger.warning.assert_called_with("No data returned for AAPL")
    assert mock_quote_service.client.aclose.await_count == 1


@pytest.mark.asyncio
async def test_fetch_symbol_data_exception_logs_error(
    mock_config,
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    mock_quote_service.fetch_historical_bars.side_effect = Exception("fail!")
    coordinator = DataIngestStageCoordinator(
        config=mock_config,
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
    )
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert results == []
    assert mock_logger.error.called
    assert mock_quote_service.client.aclose.await_count == 1
