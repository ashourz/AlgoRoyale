# tests/service/test_alpaca_client.py
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies

from algo_royale.client.alpaca_data_client import AlpacaClient

class TestAlpacaClient(TestCase):

    def setUp(self):
        patcher = patch("src.algo_royale.client.alpaca_api_client.StockHistoricalDataClient")
        self.addCleanup(patcher.stop)
        self.mock_data_client_class = patcher.start()

        # Create a mock instance and configure it
        self.mock_data_client_instance = MagicMock()
        self.mock_data_client_class.return_value = self.mock_data_client_instance

        # Set up the .get_stock_bars().df.reset_index() call chain
        mock_df = MagicMock()
        mock_df.df.reset_index.return_value = "mocked dataframe"
        self.mock_data_client_instance.get_stock_bars.return_value = mock_df

        # Now create the AlpacaClient instance AFTER patching
        self.client = AlpacaClient()

    def test_fetch_historical_data(self):
        result = self.client.fetch_historical_data(
            symbols=["AAPL"],
            start_date=datetime(2024, 4, 1),
            end_date=datetime(2024, 4, 2),
            timeframe=TimeFrame(1, TimeFrameUnit.Minute),
            sort_order=Sort.DESC,
            feed=DataFeed.IEX,
            adjustment=Adjustment.RAW
        )

        self.mock_data_client_instance.get_stock_bars.assert_called_once()
        self.assertEqual(result, "mocked dataframe")

if __name__ == "__main__":
    unittest.main()
