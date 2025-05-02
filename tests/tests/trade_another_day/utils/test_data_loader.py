import os
import pandas as pd
from unittest.mock import patch, MagicMock

from algo_royale.trade_another_day.utils.data_loader import BacktestDataLoader

# Mock Bar model
class MockBar:
    def __init__(self, timestamp, open, high, low, close, volume):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def dict(self):
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

@patch("trade_another_day.utils.data_loader.AlpacaQuoteService")
@patch("trade_another_day.utils.data_loader.load_config")
@patch("trade_another_day.utils.data_loader.load_watchlist")
def test_fetch_data_for_symbol(mock_watchlist, mock_config, mock_quote_service):
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "data_dir": "/tmp",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "interval": "1Day"
    }

    mock_service = MagicMock()
    mock_quote_service.return_value = mock_service

    mock_service.fetch_historical_bars.return_value = MagicMock(
        symbol_bars={
            "AAPL": [MockBar("2023-01-01T00:00:00Z", 100, 105, 95, 102, 1000)]
        }
    )

    loader = BacktestDataLoader()
    df = loader._fetch_data_for_symbol("AAPL")

    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns
    assert df.iloc[0]["open"] == 100


@patch("trade_another_day.utils.data_loader.pd.read_csv")
@patch("trade_another_day.utils.data_loader.os.path.exists")
@patch("trade_another_day.utils.data_loader.load_config")
@patch("trade_another_day.utils.data_loader.load_watchlist")
def test_load_symbol_reads_existing_file(mock_watchlist, mock_config, mock_exists, mock_read_csv):
    mock_watchlist.return_value = ["AAPL"]
    mock_config.return_value = {
        "data_dir": "/tmp",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "interval": "1Day"
    }

    mock_exists.return_value = True
    df_mock = pd.DataFrame([{"datetime": "2023-01-01", "open": 100}])
    mock_read_csv.return_value = df_mock

    loader = BacktestDataLoader()
    df = loader.load_symbol("AAPL", fetch_if_missing=False)

    assert df.equals(df_mock)
    mock_read_csv.assert_called_once()


@patch("trade_another_day.utils.data_loader.BacktestDataLoader.load_symbol")
@patch("trade_another_day.utils.data_loader.load_config")
@patch("trade_another_day.utils.data_loader.load_watchlist")
def test_load_all_calls_load_symbol(mock_watchlist, mock_config, mock_load_symbol):
    mock_watchlist.return_value = ["AAPL", "TSLA"]
    mock_config.return_value = {
        "data_dir": "/tmp",
        "watchlist_path": "mock/path",
        "start_date": "2023-01-01",
        "end_date": "2023-01-10",
        "interval": "1Day"
    }

    mock_load_symbol.side_effect = lambda symbol, fetch: pd.DataFrame([{"symbol": symbol}])

    loader = BacktestDataLoader()
    result = loader.load_all()

    assert "AAPL" in result
    assert "TSLA" in result
    assert isinstance(result["AAPL"], pd.DataFrame)
