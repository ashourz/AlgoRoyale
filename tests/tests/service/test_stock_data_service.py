# tests for service\stock_Data_service.py

import unittest
from unittest import TestCase
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime
from shared.service.db.stock_data_service import StockDataService

class TestStockDataService(TestCase):
    @patch("shared.service.db.stock_data_service.StockDataDAO")
    def setUp(self, MockStockDataDAO):
        """Set up mock objects and test data."""
        self.mock_dao = MockStockDataDAO.return_value
        self.service = StockDataService()
        self.service.trade_signals_dao = self.mock_dao

    def test_create_stock_data(self):
        """Test the create_stock_data method."""
        stock_data = {
            "symbol": "AAPL",
            "timestamp": datetime(2024, 4, 11, 14, 30, 0),
            "open_price": Decimal("150.00"),
            "high": Decimal("155.00"),
            "low": Decimal("149.00"),
            "close": Decimal("154.00"),
            "volume": 1000
        }

        self.service.create_stock_data(**stock_data)

        self.mock_dao.insert_stock_data.assert_called_once_with(
            "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
            Decimal("149.00"), Decimal("154.00"), 1000
        )

    def test_get_stock_data_by_symbol(self):
        """Test the get_stock_data_by_symbol method."""
        symbol = "AAPL"
        stock_data_records = [
            (1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
             Decimal("149.00"), Decimal("154.00"), 1000)
        ]

        self.mock_dao.fetch_stock_data_by_symbol.return_value = stock_data_records

        result = self.service.get_stock_data_by_symbol(symbol)

        self.mock_dao.fetch_stock_data_by_symbol.assert_called_once_with(symbol)
        self.assertEqual(result, stock_data_records)
        
    def test_get_latest_stock_data(self):
        """Test the get_latest_stock_data method."""
        symbol = "AAPL"
        latest_stock_data_record = (1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
                                     Decimal("149.00"), Decimal("154.00"), 1000)

        self.mock_dao.fetch_latest_stock_data.return_value = latest_stock_data_record

        result = self.service.get_latest_stock_data(symbol)

        self.mock_dao.fetch_latest_stock_data.assert_called_once_with(symbol)
        self.assertEqual(result, latest_stock_data_record)
        
    def test_get_stock_data_by_symbol_and_date(self):
        """Test the get_stock_data_by_symbol_and_date method."""
        symbol = "AAPL"
        start_time = datetime(2024, 4, 1, 0, 0, 0)
        end_time = datetime(2024, 4, 30, 23, 59, 59)
        stock_data_records = [
            (1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
             Decimal("149.00"), Decimal("154.00"), 1000)
        ]
        
        self.mock_dao.fetch_stock_data_by_symbol_and_date.return_value = stock_data_records
        
        result = self.service.get_stock_data_by_symbol_and_date(symbol, start_time, end_time)
        
        self.mock_dao.fetch_stock_data_by_symbol_and_date.assert_called_once_with(symbol, start_time, end_time)
        self.assertEqual(result, stock_data_records)    
        
    def test_update_stock_data(self):
        """Test the update_stock_data method."""
        stock_data = {
            "stock_data_id": 1,
            "symbol": "AAPL",
            "timestamp": datetime(2024, 4, 11, 14, 30, 0),
            "open_price": Decimal("150.00"),
            "high": Decimal("155.00"),
            "low": Decimal("149.00"),
            "close": Decimal("154.00"),
            "volume": 1000
        }

        self.service.update_stock_data(**stock_data)

        self.mock_dao.update_stock_data.assert_called_once_with(
            1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
            Decimal("149.00"), Decimal("154.00"), 1000
        )
        
    def test_delete_stock_data(self):
        """Test the delete_stock_data method."""
        stock_data_id = 1

        self.service.delete_stock_data(stock_data_id)

        self.mock_dao.delete_stock_data.assert_called_once_with(stock_data_id)
        
    def test_get_all_stock_data(self):
        """Test the get_all_stock_data method."""
        stock_data_records = [
            (1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
             Decimal("149.00"), Decimal("154.00"), 1000)
        ]

        self.mock_dao.fetch_all_stock_data.return_value = stock_data_records

        result = self.service.get_all_stock_data()

        self.mock_dao.fetch_all_stock_data.assert_called_once()
        self.assertEqual(result, stock_data_records)
        
    def test_get_stock_data_by_symbol_no_data(self):
        """Test the get_stock_data_by_symbol method when no data is found."""
        symbol = "AAPL"
        self.mock_dao.fetch_stock_data_by_symbol.return_value = []

        result = self.service.get_stock_data_by_symbol(symbol)

        self.mock_dao.fetch_stock_data_by_symbol.assert_called_once_with(symbol)
        self.assertEqual(result, [])
        
    def test_get_stock_data_by_symbol_and_timestamp_no_data(self):
        """Test the get_stock_data_by_symbol_and_timestamp method when no data is found."""
        symbol = "AAPL"
        start_time = datetime(2024, 4, 1, 0, 0, 0)
        end_time = datetime(2024, 4, 30, 23, 59, 59)
        self.mock_dao.fetch_stock_data_by_symbol_and_date.return_value = []

        result = self.service.get_stock_data_by_symbol_and_date(symbol, start_time, end_time)

        self.mock_dao.fetch_stock_data_by_symbol_and_date.assert_called_once_with(symbol, start_time, end_time)
        self.assertEqual(result, [])
        
    def test_get_latest_stock_data_no_data(self):
        """Test the get_latest_stock_data method when no data is found."""
        symbol = "AAPL"
        self.mock_dao.fetch_latest_stock_data.return_value = None

        result = self.service.get_latest_stock_data(symbol)

        self.mock_dao.fetch_latest_stock_data.assert_called_once_with(symbol)
        self.assertIsNone(result)
        
    def test_update_stock_data_no_data(self):
        """Test the update_stock_data method when no data is found."""
        stock_data = {
            "stock_data_id": 1,
            "symbol": "AAPL",
            "timestamp": datetime(2024, 4, 11, 14, 30, 0),
            "open_price": Decimal("150.00"),
            "high": Decimal("155.00"),
            "low": Decimal("149.00"),
            "close": Decimal("154.00"),
            "volume": 1000
        }

        self.mock_dao.update_stock_data.return_value = None

        self.service.update_stock_data(**stock_data)

        self.mock_dao.update_stock_data.assert_called_once_with(
            1, "AAPL", datetime(2024, 4, 11, 14, 30, 0), Decimal("150.00"), Decimal("155.00"),
            Decimal("149.00"), Decimal("154.00"), 1000
        )
        
    def test_delete_stock_data_no_data(self):
        """Test the delete_stock_data method when no data is found."""
        stock_data_id = 1

        self.mock_dao.delete_stock_data.return_value = None

        self.service.delete_stock_data(stock_data_id)

        self.mock_dao.delete_stock_data.assert_called_once_with(stock_data_id)
    
    
    def tearDown(self):
        """Clean up mock objects."""
        self.mock_dao.reset_mock()
        self.service = None

if __name__ == "__main__":
    unittest.main()
