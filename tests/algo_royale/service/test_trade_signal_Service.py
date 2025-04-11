# tests for service\trade_signal_Service.py

import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from src.algo_royale.service.trade_signal_service import TradeSignalService


class TestTradeSignalService(TestCase):
    @patch("src.algo_royale.service.trade_signal_service.TradeSignalsDAO")
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


if __name__ == "__main__":
    unittest.main()
