# tests/test_trade_service.py
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from src.algo_royale.service.trade_service import TradeService
from decimal import Decimal
from datetime import datetime

class TestTradeService(TestCase):

    @patch("src.algo_royale.service.trade_service.TradesDAO")
    def setUp(self, MockTradesDAO):
        self.mock_dao = MockTradesDAO.return_value
        self.service = TradeService()

    def test_create_trade(self):
        # Arrange
        symbol = "AAPL"
        trade_type = "BUY"
        price = Decimal("150.00")
        quantity = 10
        phase = "Phase1"
        timestamp = datetime(2024, 4, 11, 0)
        notes = "Note1"

        # Act
        self.service.create_trade(symbol, trade_type, price, quantity, phase, timestamp, notes)

        # Assert
        self.mock_dao.insert_trade.assert_called_once_with(symbol, trade_type, price, quantity, phase, timestamp, notes)

    def test_get_trade_history(self):
        # Arrange
        expected_result = [
            (1, "AAPL", "BUY", Decimal("150.00"), 10, "Phase1", datetime(2024, 4, 11, 0), "Note1"),
            (2, "GOOGL", "SELL", Decimal("2800.00"), 5, "Phase2", datetime(2024, 4, 12, 0), "Note2"),
        ]
        self.mock_dao.fetch_all_trades.return_value = expected_result

        # Act
        result = self.service.get_trade_history()

        # Assert
        self.assertEqual(result, expected_result)
        self.mock_dao.fetch_all_trades.assert_called_once()

    def test_delete_trade(self):
        # Act
        self.service.delete_trade(1)

        # Assert
        self.mock_dao.delete_trade.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()