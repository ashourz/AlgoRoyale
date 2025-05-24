from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from algo_royale.di.container import di_container


class MockBar:
    def __init__(self, timestamp, open, high, low, close, volume):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def model_dump(self):
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@patch("algo_royale.di.container.DIContainer.config")
@patch("algo_royale.services.market_data.alpaca_stock_service.AlpacaQuoteService")
@patch("algo_royale.backtester.watchlist.watchlist.load_watchlist")
@pytest.mark.asyncio
async def test_fetch_and_save_symbol(mock_watchlist, mock_quote_service, mock_config):
    # Mock configuration and watchlist
    mock_watchlist.return_value = ["AAPL"]
    mock_config().get.side_effect = lambda section, key: {
        "paths.backtester": {
            "data_ingest_dir": "/tmp/test_data",
            "watchlist_path": "mock/path",
        },
        "backtest": {
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
        },
    }[section][key]

    # Mock AlpacaQuoteService response
    mock_response = AsyncMock()
    mock_response.symbol_bars = {
        "AAPL": [MockBar("2023-01-01T00:00:00Z", 100, 105, 95, 102, 1000)],
    }
    mock_response.next_page_token = None

    mock_service = AsyncMock()
    mock_service.fetch_historical_bars.return_value = mock_response
    mock_quote_service.return_value = mock_service

    # Initialize BacktestDataLoader
    loader = di_container.stage_data_loader()

    # Create mock logger
    mock_logger = MagicMock()
    loader.logger = mock_logger

    # Test the method
    result = await loader._fetch_and_save_symbol("AAPL")

    assert result is True
    expected_file = Path(loader.data_dir) / "AAPL" / "AAPL_page_1.csv"
    assert expected_file.exists()


@patch("algo_royale.di.container.DIContainer.config")
@patch("algo_royale.services.market_data.alpaca_stock_service.AlpacaQuoteService")
@patch("algo_royale.backtester.watchlist.watchlist.load_watchlist")
@pytest.mark.asyncio
async def test_load_all_calls_load_symbol(
    mock_watchlist, mock_quote_service, mock_config
):
    # Mock configuration and watchlist
    mock_watchlist.return_value = ["AAPL", "TSLA"]
    mock_config().get.side_effect = lambda section, key: {
        "paths.backtester": {
            "data_ingest_dir": "/tmp/test_data",
            "watchlist_path": "mock/path",
        },
        "backtest": {
            "start_date": "2023-01-01",
            "end_date": "2023-01-10",
        },
    }[section][key]

    # Mock AlpacaQuoteService
    mock_quote_service.return_value = AsyncMock()

    # Initialize BacktestDataLoader
    loader = di_container.stage_data_loader()

    # Create mock logger
    mock_logger = MagicMock()
    loader.logger = mock_logger

    # Mock _fetch_and_save_symbol and load_symbol
    async def mock_load_symbol(symbol):
        return iter([pd.DataFrame([{"timestamp": "2023-01-01", "open": 100}])])

    loader.load_symbol = mock_load_symbol

    # Test load_all method
    result = await loader.load_all()

    assert "AAPL" in result
    assert "TSLA" in result
    assert callable(result["AAPL"])
    assert callable(result["TSLA"])


@patch("algo_royale.di.container.DIContainer.config")
@patch("algo_royale.services.market_data.alpaca_stock_service.AlpacaQuoteService")
@patch("algo_royale.backtester.watchlist.watchlist.load_watchlist")
@pytest.mark.asyncio
async def test_load_symbol_reads_existing_pages(
    mock_watchlist, mock_quote_service, mock_config
):
    # Mock configuration and watchlist
    mock_watchlist.return_value = ["AAPL"]
    mock_config().get.side_effect = lambda section, key: {
        "paths.backtester": {
            "data_ingest_dir": "/tmp/test_data",
            "watchlist_path": "mock/path",
        },
        "backtest": {
            "start_date": "2023-01-01",
            "end_date": "2023-01-10",
        },
    }[section][key]

    # Mock AlpacaQuoteService
    mock_quote_service.return_value = AsyncMock()

    # Initialize BacktestDataLoader
    loader = di_container.stage_data_loader()

    # Create mock logger
    mock_logger = MagicMock()
    loader.logger = mock_logger

    # Mock existing files
    mock_csv_1 = pd.DataFrame([{"timestamp": "2023-01-01T00:00:00Z", "open": 100}])
    mock_csv_2 = pd.DataFrame([{"timestamp": "2023-01-02T00:00:00Z", "open": 105}])

    async def mock_stream_existing_data_async(symbol_dir):
        # Simulate the async generator behavior
        yield mock_csv_1
        yield mock_csv_2

    loader._stream_existing_data_async = mock_stream_existing_data_async

    # Test load_symbol
    dfs = []
    async for df in loader.load_symbol("AAPL"):
        dfs.append(df)

    # Assertions
    assert len(dfs) == 2
    assert dfs[0].equals(mock_csv_1)
    assert dfs[1].equals(mock_csv_2)
