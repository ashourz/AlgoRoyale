import types
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
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
def mock_quote_service():
    return MagicMock()


def test_init_success(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    # Should not raise
    DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist.txt",
    )


def test_init_missing_watchlist_path(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: ["AAPL"],
            watchlist_path_string="",  # missing path
        )


def test_init_empty_watchlist(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            data_loader=mock_loader,
            data_preparer=mock_preparer,
            data_writer=mock_writer,
            stage_data_manager=mock_manager,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: [],
            watchlist_path_string="mock_watchlist.txt",
        )


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist.txt",
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    result = await coordinator.process(prepared_data=None)
    assert "AAPL" in result and "GOOG" in result


@pytest.mark.asyncio
async def test_fetch_symbol_data_success(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
    monkeypatch,
):
    import algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator as dic_mod

    # Patch required enums/constants
    monkeypatch.setattr(
        dic_mod, "SupportedCurrencies", types.SimpleNamespace(USD="USD")
    )
    monkeypatch.setattr(dic_mod, "DataFeed", types.SimpleNamespace(IEX="IEX"))
    monkeypatch.setattr(
        dic_mod, "DataIngestColumns", types.SimpleNamespace(SYMBOL="symbol")
    )

    class DummyBar:
        def model_dump(self):
            return {"open": 1, "close": 2}

    class DummyResponse:
        def __init__(self, bars, next_page_token=None):
            self.symbol_bars = {"AAPL": bars}
            self.next_page_token = next_page_token

    # Use a function for side_effect to handle any arguments
    responses = [
        DummyResponse([DummyBar(), DummyBar()], next_page_token="token2"),
        DummyResponse([DummyBar()], next_page_token=None),
    ]

    def fetch_historical_bars_side_effect(*args, **kwargs):
        return responses.pop(0) if responses else DummyResponse([])

    mock_quote_service.fetch_historical_bars = AsyncMock(
        side_effect=fetch_historical_bars_side_effect
    )

    coordinator = dic_mod.DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist.txt",
    )
    coordinator.quote_service.client = MagicMock()
    coordinator.quote_service.client.aclose = AsyncMock()
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_fetch_symbol_data_no_data_warns(
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
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist.txt",
    )
    coordinator.quote_service.client = MagicMock()
    coordinator.quote_service.client.aclose = AsyncMock()
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert results == []


@pytest.mark.asyncio
async def test_fetch_symbol_data_exception_logs_error(
    mock_loader,
    mock_preparer,
    mock_writer,
    mock_manager,
    mock_logger,
    mock_quote_service,
):
    mock_quote_service.fetch_historical_bars.side_effect = Exception("fail!")
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_preparer=mock_preparer,
        data_writer=mock_writer,
        stage_data_manager=mock_manager,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist.txt",
    )
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    with pytest.raises(Exception):
        async for df in coordinator._fetch_symbol_data("AAPL"):
            results.append(df)
