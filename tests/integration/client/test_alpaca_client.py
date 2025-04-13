# src: tests/integration/client/test_alpaca_client.py
import unittest
from datetime import datetime
from src.algo_royale.client.alpaca_api_client import AlpacaClient  # Import your AlpacaClient class

class TestAlpacaClientIntegration(unittest.TestCase):
    def setUp(self):
        """Initialize the AlpacaClient with live trading data."""
        # Ensure you're using the live environment or paper trading based on your configuration
        self.alpaca_client = AlpacaClient(use_paper=True)  # Set use_paper=False for live trading

    def test_fetch_historical_data(self):
        """Test fetching historical data from Alpaca's live endpoint."""
        symbols = ["AAPL"]  # You can add more symbols as needed
        start_date = datetime(2024, 4, 1)
        end_date = datetime(2024, 4, 3)
        timeframe = "1Min"  # Timeframe for historical data
        sort_order = "asc"  # Ascending or descending order for sorting
        
        # Fetch the data from Alpaca's API
        result = self.alpaca_client.fetch_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
            sort_order=sort_order
        )
        
        # Assertions: Validate that the data returned is correct
        self.assertIsNotNone(result)  # Ensure some result was returned
        self.assertGreater(len(result), 0)  # Ensure there's at least one data point
        
        # Optional: Check specific aspects of the data
        print(result.head())  # Output the first few rows for inspection
        self.assertIn("time", result.columns)  # Ensure the expected columns exist
        self.assertIn("open", result.columns)
        self.assertIn("close", result.columns)

    def test_invalid_date(self):
        """Test invalid date range handling."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 5)
        end_date = datetime(2024, 4, 1)  # End date before start date (invalid)
        
        with self.assertRaises(ValueError):
            self.alpaca_client.fetch_historical_data(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date
            )

    def test_no_data_for_symbol(self):
        """Test fetching data for a symbol that has no historical data."""
        symbols = ["NONEXISTENT"]  # A symbol that doesn't exist or has no data
        start_date = datetime(2024, 4, 1)
        end_date = datetime(2024, 4, 3)
        
        result = self.alpaca_client.fetch_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertEqual(len(result), 0)  # No data should be returned

if __name__ == "__main__":
    unittest.main()
