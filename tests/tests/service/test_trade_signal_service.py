# tests for service\trade_signal_Service.py

import unittest
from unittest import TestCase
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime
from algo_royale.shared.service.db.trade_signal_service import TradeSignalService


class TestTradeSignalService(TestCase):
    @patch("algo_royale.shared.service.db.trade_signal_service.TradeSignalsDAO")
    def setUp(self, MockTradeSignalsDAO):
        """Set up mock objects and test data."""
        self.mock_dao = MockTradeSignalsDAO.return_value
        self.service = TradeSignalService()
        self.service.trade_signals_dao = self.mock_dao


    def test_create_signal(self):
        """Test the create_signal method."""
        signal_data = {
            "symbol": "AAPL",
            "signal": "BUY",
            "price": Decimal("150.00"),
            "created_at": datetime(2024, 4, 11, 14, 30, 0)
        }

        self.service.create_signal(**signal_data)

        self.mock_dao.insert_signal.assert_called_once_with(
            "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0)
        )

    def test_get_signals_by_symbol(self):
        """Test the get_signals_by_symbol method."""
        symbol = "AAPL"
        signal_records = [
            (1, "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0)),
            (2, "AAPL", "SELL", Decimal("155.00"), datetime(2024, 4, 12, 14, 30, 0))
        ]

        self.mock_dao.fetch_signals_by_symbol.return_value = signal_records

        result = self.service.get_signals_by_symbol(symbol)

        self.mock_dao.fetch_signals_by_symbol.assert_called_once_with(symbol)
        self.assertEqual(result, signal_records)

    def test_get_signal_by_id(self):
        """Test the get_signal_by_id method."""
        signal_id = 1
        signal_record = (1, "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0))

        self.mock_dao.fetch_signal_by_id.return_value = signal_record

        result = self.service.get_signal_by_id(signal_id)

        self.mock_dao.fetch_signal_by_id.assert_called_once_with(signal_id)
        self.assertEqual(result, signal_record)

    def test_get_all_signals(self):
        """Test the get_all_signals method."""
        signal_records = [
            (1, "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0)),
            (2, "AAPL", "SELL", Decimal("155.00"), datetime(2024, 4, 12, 14, 30, 0))
        ]

        self.mock_dao.fetch_all_signals.return_value = signal_records

        result = self.service.get_all_signals()

        self.mock_dao.fetch_all_signals.assert_called_once()
        self.assertEqual(result, signal_records)
        
    def test_update_signal(self):
        """Test the update_signal method."""
        signal_data = {
            "signal_id": 1,
            "symbol": "AAPL",
            "signal": "BUY",
            "price": Decimal("150.00"),
            "created_at": datetime(2024, 4, 11, 14, 30, 0)
        }

        self.service.update_signal(**signal_data)

        self.mock_dao.update_signal.assert_called_once_with(
            1, "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0)
        )
    
    def test_delete_signal(self):
        """Test the delete_signal method."""
        signal_id = 1

        self.service.delete_signal(signal_id)

        self.mock_dao.delete_signal.assert_called_once_with(signal_id)
        
    def test_get_signal_by_symbol_and_date(self):
        """Test the get_signal_by_symbol_and_date method."""
        symbol = "AAPL"
        start_date = datetime(2024, 4, 11, 0, 0, 0)
        end_date = datetime(2024, 4, 12, 23, 59, 59)
        signal_records = [
            (1, "AAPL", "BUY", Decimal("150.00"), datetime(2024, 4, 11, 14, 30, 0)),
            (2, "AAPL", "SELL", Decimal("155.00"), datetime(2024, 4, 12, 14, 30, 0))
        ]

        self.mock_dao.fetch_signals_by_symbol_and_date.return_value = signal_records

        result = self.service.get_signal_by_symbol_and_date(symbol, start_date, end_date)

        self.mock_dao.fetch_signals_by_symbol_and_date.assert_called_once_with(
            symbol, start_date, end_date
        )
        self.assertEqual(result, signal_records)        
        
    
    def test_get_signal_by_symbol_and_date_no_records(self):
        """Test the get_signal_by_symbol_and_date method with no records."""
        symbol = "AAPL"
        start_date = datetime(2024, 4, 11, 0, 0, 0)
        end_date = datetime(2024, 4, 12, 23, 59, 59)

        self.mock_dao.fetch_signals_by_symbol_and_date.return_value = []

        result = self.service.get_signal_by_symbol_and_date(symbol, start_date, end_date)

        self.mock_dao.fetch_signals_by_symbol_and_date.assert_called_once_with(
            symbol, start_date, end_date
        )
        self.assertEqual(result, [])
        
    def test_get_signals_by_symbol_no_records(self):
        """Test the get_signals_by_symbol method with no records."""
        symbol = "AAPL"

        self.mock_dao.fetch_signals_by_symbol.return_value = []

        result = self.service.get_signals_by_symbol(symbol)

        self.mock_dao.fetch_signals_by_symbol.assert_called_once_with(symbol)
        self.assertEqual(result, [])    
    
    def test_get_signal_by_id_not_found(self):
        """Test the get_signal_by_id method when signal ID is not found."""
        signal_id = 999
        self.mock_dao.fetch_signal_by_id.return_value = None
        
    def tearDown(self):
        """Clean up mock objects."""
        self.mock_dao.reset_mock()
        self.service = None

if __name__ == "__main__":
    unittest.main()
