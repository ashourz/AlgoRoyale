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
        self.service.create_trade(
            symbol="AAPL",
            direction="BUY",
            entry_price=Decimal("150.00"),
            shares=10,
            strategy_phase="Phase1",
            entry_time=datetime(2024, 4, 11),
            notes="test note"
        )
        self.mock_dao.insert_trade.assert_called_once_with(
            "AAPL", "BUY", Decimal("150.00"), 10, "Phase1", datetime(2024, 4, 11), "test note"
        )

    def test_update_trade(self):
        self.service.update_trade(
            trade_id=1,
            exit_price=Decimal("160.00"),
            exit_time=datetime(2024, 4, 12),
            pnl=Decimal("100.00")
        )
        self.mock_dao.update_trade.assert_called_once_with(
            1, Decimal("160.00"), datetime(2024, 4, 12), Decimal("100.00")
        )

    def test_get_trade_by_id(self):
        self.mock_dao.fetch_trade_by_id.return_value = ("mock_trade",)
        result = self.service.get_trade_by_id(42)
        self.mock_dao.fetch_trade_by_id.assert_called_once_with(42)
        self.assertEqual(result, ("mock_trade",))

    def test_calculate_trade_pnl(self):
        result = self.service.calculate_trade_pnl(
            entry_price=Decimal("100.00"),
            exit_price=Decimal("120.00"),
            shares=5
        )
        self.assertEqual(result, Decimal("100.00"))

    def test_get_trade_history(self):
        self.mock_dao.fetch_all_trades.return_value = [("mock_trade_1",), ("mock_trade_2",)]
        result = self.service.get_trade_history()
        self.mock_dao.fetch_all_trades.assert_called_once()
        self.assertEqual(result, [("mock_trade_1",), ("mock_trade_2",)])

    def test_delete_trade(self):
        self.service.delete_trade(99)
        self.mock_dao.delete_trade.assert_called_once_with(99)


if __name__ == "__main__":
    unittest.main()