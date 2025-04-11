# tests for service\indicators_sentiment_service.py

import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from src.algo_royale.service.indicator_service import IndicatorService

class TestIndicatorsService(TestCase):
    @patch("src.algo_royale.service.indicator_service.IndicatorDAO")
    def setUp(self, MockIndicatorDAO):
        """Set up mock objects and test data."""
        self.mock_dao = MockIndicatorDAO.return_value
        self.service = IndicatorService()
        self.service.indicators_dao = self.mock_dao
        
    def test_create_indicator(self):
        self.service.create_indicator(
            trade_id=1,
            rsi=Decimal("70.1"),
            macd=Decimal("1.2"),
            macd_signal=Decimal("1.0"),
            volume=Decimal("1000000"),
            bollinger_upper=Decimal("150"),
            bollinger_lower=Decimal("120"),
            atr=Decimal("2.5"),
            price=Decimal("145"),
            ema_short=Decimal("143"),
            ema_long=Decimal("140"),
            recorded_at=datetime(2024, 4, 11, 12, 0)
        )

        self.mock_dao.insert_indicator.assert_called_once()

    def test_get_indicators_by_trade_id(self):
        trade_id = 1
        expected = [(1, 1, Decimal("70.1"), Decimal("1.2"), Decimal("1.0"),
                     Decimal("1000000"), Decimal("150"), Decimal("120"),
                     Decimal("2.5"), Decimal("145"), Decimal("143"), Decimal("140"),
                     datetime(2024, 4, 11, 12, 0))]

        self.mock_dao.fetch_indicators_by_trade_id.return_value = expected

        result = self.service.get_indicators_by_trade_id(trade_id)

        self.mock_dao.fetch_indicators_by_trade_id.assert_called_once_with(trade_id)
        self.assertEqual(result, expected)

    def test_update_indicator(self):
        self.service.update_indicator(
            indicator_id=99,
            rsi=Decimal("60"),
            macd=Decimal("1.1"),
            macd_signal=Decimal("1.05"),
            volume=Decimal("900000"),
            bollinger_upper=Decimal("148"),
            bollinger_lower=Decimal("122"),
            atr=Decimal("2.0"),
            price=Decimal("143"),
            ema_short=Decimal("142"),
            ema_long=Decimal("139"),
            recorded_at=datetime(2024, 4, 11, 13, 0)
        )

        self.mock_dao.update_indicator.assert_called_once()

    def test_delete_indicator(self):
        self.service.delete_indicator(77)
        self.mock_dao.delete_indicator.assert_called_once_with(77)

        
if __name__ == "__main__":
    unittest.main()