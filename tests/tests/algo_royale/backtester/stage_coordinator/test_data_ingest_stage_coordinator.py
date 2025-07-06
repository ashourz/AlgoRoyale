import types
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)


@pytest.fixture
def mock_loader():
    return MagicMock()


@pytest.fixture
def mock_writer():
    return MagicMock()


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_quote_service():
    return MagicMock()


def test_init_success(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    # Should not raise
    DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist.txt",
    )


def test_init_missing_watchlist_path(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    with pytest.raises(ValueError):
        DataIngestStageCoordinator(
            data_loader=mock_loader,
            data_writer=mock_writer,
            logger=mock_logger,
            quote_service=mock_quote_service,
            load_watchlist=lambda path: ["AAPL"],
            watchlist_path_string="",
        )


def test_init_empty_watchlist(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    mock_loader.get_watchlist.return_value = []
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: [],
        watchlist_path_string="mock_watchlist.txt",
    )
    with pytest.raises(
        ValueError,
        match="Watchlist loaded from mock_watchlist.txt is empty. Cannot proceed with data ingestion.",
    ):
        coordinator._get_watchlist()


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    mock_loader.get_watchlist.return_value = ["AAPL", "GOOG"]
    mock_writer.write_symbol_strategy_data_factory = AsyncMock(return_value=True)
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL", "GOOG"],
        watchlist_path_string="mock_watchlist.txt",
    )
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    result = await coordinator.run(start_date=start_date, end_date=end_date)
    assert result is True


@pytest.mark.asyncio
async def test_fetch_symbol_data_success(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
    monkeypatch,
):
    # Patch required enums/constants
    import algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator as dic_mod

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
        data_writer=mock_writer,
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
    mock_writer,
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
        data_writer=mock_writer,
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
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    mock_quote_service.fetch_historical_bars.side_effect = Exception("fail!")
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        logger=mock_logger,
        quote_service=mock_quote_service,
        load_watchlist=lambda path: ["AAPL"],
        watchlist_path_string="mock_watchlist.txt",
    )
    coordinator.quote_service.client = MagicMock()
    coordinator.quote_service.client.aclose = AsyncMock()
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    # Should not raise, but should log error
    results = []
    async for _ in coordinator._fetch_symbol_data("AAPL"):
        results.append(_)
    # Should be empty due to exception
    assert results == []
