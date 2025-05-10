from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import pandas as pd
import pytest
from algo_royale.trade_another_day.utils.data_loader import BacktestDataLoader

# Mock Bar model with model_dump (used in updated version)
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
            "volume": self.volume
        }


@patch("algo_royale.trade_another_day.utils.data_loader.AlpacaQuoteService")
@patch("algo_royale.trade_another_day.utils.data_loader.load_paths")
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
@pytest.mark.asyncio
async def test_fetch_and_save_symbol(mock_watchlist, mock_config, mock_paths, mock_quote_service):
    # Mock configuration and paths
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-02",
    }
    mock_paths.return_value = {
        "data_ingest_dir": "/tmp/test_data",
        "watchlist_path": "mock/path",
    }

    # Mock AlpacaQuoteService response
    mock_response = AsyncMock()
    mock_response.symbol_bars = {
        "AAPL": [MockBar("2023-01-01T00:00:00Z", 100, 105, 95, 102, 1000)]
    }
    mock_response.next_page_token = None

    mock_service = AsyncMock()
    mock_service.fetch_historical_bars.return_value = mock_response
    mock_quote_service.return_value = mock_service

    # Create the loader and test the method
    loader = BacktestDataLoader()
    result = await loader._fetch_and_save_symbol("AAPL")

    assert result is True
    expected_file = Path(loader.data_dir) / "AAPL" / "AAPL_page_1.csv"
    assert expected_file.exists()


@patch("algo_royale.trade_another_day.utils.data_loader.Path.glob")
@patch("algo_royale.trade_another_day.utils.data_loader.os.path.exists")
@patch("algo_royale.trade_another_day.utils.data_loader.load_paths")
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
@patch("algo_royale.trade_another_day.utils.data_loader.pd.read_csv")
@pytest.mark.asyncio
async def test_load_symbol_reads_existing_pages(
    mock_read_csv, mock_watchlist, mock_config, mock_paths, mock_exists, mock_glob
):
    # Mock watchlist, configuration, and paths
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
    }
    mock_paths.return_value = {
        "data_ingest_dir": "/tmp/test_data",
        "watchlist_path": "mock/path",
    }

    # Mock file existence
    mock_exists.side_effect = lambda path: path == "/tmp/test_data/AAPL"

    # Mock Path.glob to simulate existing CSV files
    mock_glob.return_value = [
        Path("/tmp/test_data/AAPL/AAPL_page_1.csv"),
        Path("/tmp/test_data/AAPL/AAPL_page_2.csv"),
    ]

    # Mock DataFrame reading
    mock_df_page_1 = pd.DataFrame([{"timestamp": "2023-01-01T00:00:00Z", "open": 100}])
    mock_df_page_2 = pd.DataFrame([{"timestamp": "2023-01-02T00:00:00Z", "open": 105}])

    def read_csv_side_effect(filepath, *args, **kwargs):
        if "AAPL_page_1.csv" in str(filepath):
            return mock_df_page_1
        if "AAPL_page_2.csv" in str(filepath):
            return mock_df_page_2
        return pd.DataFrame()

    mock_read_csv.side_effect = read_csv_side_effect

    # Create the loader and test the method
    loader = BacktestDataLoader()
    dfs = []
    async for df in loader.load_symbol("AAPL"):
        dfs.append(df)

    # Assertions
    assert len(dfs) == 2
    assert dfs[0].equals(mock_df_page_1)
    assert dfs[1].equals(mock_df_page_2)


@patch("algo_royale.trade_another_day.utils.data_loader.BacktestDataLoader.load_symbol")
@patch("algo_royale.trade_another_day.utils.data_loader.load_paths")
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
@pytest.mark.asyncio
async def test_load_all_calls_load_symbol(mock_watchlist, mock_config, mock_paths, mock_load_symbol):
    # Mock watchlist, configuration, and paths
    mock_watchlist.return_value = ["AAPL", "TSLA"]
    mock_config.return_value = {
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
    }
    mock_paths.return_value = {
        "data_ingest_dir": "/tmp/test_data",
        "watchlist_path": "mock/path",
    }

    # Mock load_symbol to return an async generator
    mock_df = pd.DataFrame([{"timestamp": "2023-01-01", "open": 100}])
    mock_load_symbol.side_effect = lambda symbol: iter([mock_df])

    # Create the loader and test the method
    loader = BacktestDataLoader()
    result = await loader.load_all()

    # Assertions
    assert "AAPL" in result
    assert "TSLA" in result