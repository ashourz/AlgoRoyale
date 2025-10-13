import types
from datetime import datetime

import pytest

from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from tests.mocks.adapters.mock_quote_adapter import MockQuoteAdapter
from tests.mocks.backtester.mock_stage_data_manager import MockStageDataManager
from tests.mocks.backtester.stage_data.loader.mock_stage_data_loader import (
    MockStageDataLoader,
)
from tests.mocks.backtester.stage_data.writer.mock_symbol_strategy_data_writer import (
    MockSymbolStrategyDataWriter,
)
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_watchlist_repo import MockWatchlistRepo


@pytest.fixture
def mock_loader():
    return MockStageDataLoader()


@pytest.fixture
def mock_writer():
    return MockSymbolStrategyDataWriter()


@pytest.fixture
def mock_logger():
    return MockLoggable()


@pytest.fixture
def mock_quote_service():
    return MockQuoteAdapter()


@pytest.fixture
def mock_data_manager():
    return MockStageDataManager()


@pytest.fixture
def mock_watchlist_repo():
    return MockWatchlistRepo()


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
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=MockWatchlistRepo(),
    )


def test_init_missing_watchlist_path(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    with pytest.raises(FileNotFoundError):
        DataIngestStageCoordinator(
            data_loader=mock_loader,
            data_writer=mock_writer,
            data_manager=MockStageDataManager(),
            logger=mock_logger,
            quote_adapter=mock_quote_service,
            watchlist_repo=MockWatchlistRepo(
                watchlist_path="nonexistent.txt", logger=mock_logger
            ),
        )


@pytest.mark.asyncio
async def test_init_empty_watchlist(
    mock_loader, mock_writer, mock_logger, mock_quote_service
):
    """Test that an empty watchlist raises a ValueError."""
    # Patch the mock_watchlist_repo to return empty
    repo = MockWatchlistRepo()
    repo.set_return_empty(True)
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
    )
    # Patch the coordinator to have a watchlist_path attribute for error message compatibility
    coordinator.watchlist_path = "mock_watchlist.txt"
    with pytest.raises(
        ValueError,
        match="Watchlist loaded from .* is empty. Cannot proceed with data ingestion.",
    ):
        coordinator._get_watchlist()


@pytest.mark.asyncio
async def test_process_returns_factories(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
):
    """Test that the process returns factories successfully."""
    repo = MockWatchlistRepo()
    repo.test_watchlist = ["AAPL", "GOOG"]

    async def dummy_write_symbol_strategy_data_factory(*args, **kwargs):
        return True

    mock_writer.async_write_symbol_strategy_data_factory = (
        dummy_write_symbol_strategy_data_factory
    )
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
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
    """Test that fetching symbol data yields the correct number of DataFrames."""
    import algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator as dic_mod

    monkeypatch.setattr(
        dic_mod, "SupportedCurrencies", types.SimpleNamespace(USD="USD")
    )
    monkeypatch.setattr(dic_mod, "DataFeed", types.SimpleNamespace(IEX="IEX"))
    monkeypatch.setattr(
        dic_mod,
        "DataIngestColumns",
        types.SimpleNamespace(SYMBOL="symbol", OPEN="open", CLOSE="close"),
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
        return responses.pop(0) if responses else None

    async def fetch_historical_bars_async(*args, **kwargs):
        return fetch_historical_bars_side_effect(*args, **kwargs)

    mock_quote_service.fetch_historical_bars = fetch_historical_bars_async

    repo = MockWatchlistRepo()
    repo.test_watchlist = ["AAPL"]
    coordinator = dic_mod.DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
    )

    class DummyClient:
        async def aclose(self):
            pass

    coordinator.quote_adapter.client = DummyClient()
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

    async def fetch_historical_bars_async(*args, **kwargs):
        return None

    mock_quote_service.fetch_historical_bars = fetch_historical_bars_async
    repo = MockWatchlistRepo()
    repo.test_watchlist = ["AAPL"]
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
    )

    class DummyClient:
        async def aclose(self):
            pass

    coordinator.quote_adapter.client = DummyClient()
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
    async def fetch_historical_bars_async(*args, **kwargs):
        raise Exception("fail!")

    mock_quote_service.fetch_historical_bars = fetch_historical_bars_async
    repo = MockWatchlistRepo()
    repo.test_watchlist = ["AAPL"]
    coordinator = DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
    )

    class DummyClient:
        async def aclose(self):
            pass

    coordinator.quote_adapter.client = DummyClient()
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert results == []


@pytest.mark.asyncio
async def test_fetch_symbol_data_validation(
    mock_loader,
    mock_writer,
    mock_logger,
    mock_quote_service,
    monkeypatch,
):
    """Test that validation of symbol data is applied correctly."""
    import algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator as dic_mod

    monkeypatch.setattr(
        dic_mod, "SupportedCurrencies", types.SimpleNamespace(USD="USD")
    )
    monkeypatch.setattr(dic_mod, "DataFeed", types.SimpleNamespace(IEX="IEX"))
    monkeypatch.setattr(
        dic_mod,
        "DataIngestColumns",
        types.SimpleNamespace(SYMBOL="symbol", OPEN="open", CLOSE="close"),
    )

    class DummyBar:
        def model_dump(self):
            return {"open": 1, "close": 2}

    class InvalidBar:
        def model_dump(self):
            return {"invalid_column": 1}

    class DummyResponse:
        def __init__(self, bars, next_page_token=None):
            self.symbol_bars = {"AAPL": bars}
            self.next_page_token = next_page_token

    responses = [
        DummyResponse([DummyBar(), InvalidBar()], next_page_token="token2"),
        DummyResponse([DummyBar()], next_page_token=None),
    ]

    def fetch_historical_bars_side_effect(*args, **kwargs):
        return responses.pop(0) if responses else None

    async def fetch_historical_bars_async2(*args, **kwargs):
        return fetch_historical_bars_side_effect(*args, **kwargs)

    mock_quote_service.fetch_historical_bars = fetch_historical_bars_async2

    repo = MockWatchlistRepo()
    repo.test_watchlist = ["AAPL"]
    coordinator = dic_mod.DataIngestStageCoordinator(
        data_loader=mock_loader,
        data_writer=mock_writer,
        data_manager=MockStageDataManager(),
        logger=mock_logger,
        quote_adapter=mock_quote_service,
        watchlist_repo=repo,
    )

    class DummyClient:
        async def aclose(self):
            pass

    coordinator.quote_adapter.client = DummyClient()
    coordinator.start_date = datetime(2024, 1, 1)
    coordinator.end_date = datetime(2024, 1, 31)
    results = []
    async for df in coordinator._fetch_symbol_data("AAPL"):
        results.append(df)
    assert len(results) == 2
    assert "invalid_column" not in results[0].columns
