import os
from typing import Iterator
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import builtins

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
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
def test_fetch_and_save_symbol(mock_watchlist, mock_config, mock_quote_service):
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "data_dir": "/tmp/test_data",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-02",
        "interval": "1Day"
    }

    mock_response = MagicMock()
    mock_response.symbol_bars = {
        "AAPL": [MockBar("2023-01-01T00:00:00Z", 100, 105, 95, 102, 1000)]
    }
    mock_response.next_page_token = None

    mock_service = MagicMock()
    mock_service.fetch_historical_bars.return_value = mock_response
    mock_quote_service.return_value = mock_service

    loader = BacktestDataLoader()
    result = loader._fetch_and_save_symbol("AAPL")

    assert result is True
    expected_file = os.path.join(loader.data_dir, "AAPL", "AAPL_page_1.csv")
    assert os.path.exists(expected_file)

@patch("builtins.open", new_callable=mock_open, read_data="timestamp,open\n2023-01-01T00:00:00Z,100")
@patch("algo_royale.trade_another_day.utils.data_loader.pd.read_csv")
@patch("algo_royale.trade_another_day.utils.data_loader.os.path.exists")
@patch("algo_royale.trade_another_day.utils.data_loader.os.listdir")
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
async def test_load_symbol_reads_existing_pages(
    mock_watchlist,
    mock_config,
    mock_listdir,
    mock_exists,
    mock_read_csv,
    mock_file_open
):
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "data_dir": "/tmp",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "interval": "1Day"
    }

    # Return True only when checking if symbol directory exists
    def exists_side_effect(path):
        return path == os.path.join("/tmp", "AAPL")

    mock_exists.side_effect = exists_side_effect
    mock_listdir.return_value = ["AAPL_page_1.csv", "AAPL_page_2.csv"]

    mock_df = pd.DataFrame([{"timestamp": "2023-01-01T00:00:00Z", "open": 100}])
    mock_read_csv.return_value = mock_df

    loader = BacktestDataLoader()
    dfs = list(await loader.load_symbol("AAPL"))

    assert len(dfs) == 2
    for df in dfs:
        assert df.equals(mock_df)


@patch("algo_royale.trade_another_day.utils.data_loader.BacktestDataLoader.load_symbol")
@patch("algo_royale.trade_another_day.utils.data_loader.load_config")
@patch("algo_royale.trade_another_day.utils.data_loader.load_watchlist")
async def test_load_all_calls_load_symbol(mock_watchlist, mock_config, mock_load_symbol):
    mock_watchlist.return_value = ["AAPL", "TSLA"]
    mock_config.return_value = {
        "data_dir": "/tmp",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "interval": "1Day"
    }

    mock_df = pd.DataFrame([{"timestamp": "2023-01-01", "open": 100}])
    mock_load_symbol.side_effect = lambda symbol: iter([mock_df])

    loader = BacktestDataLoader()
    result = await loader.load_all()

    assert "AAPL" in result
    assert "TSLA" in result
    assert isinstance(result["AAPL"], Iterator)
