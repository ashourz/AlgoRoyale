# tests for service\news_sentiment_service.py

import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from src.service.news_sentiment_service import NewsSentimentService

class TestNewsSentimentService(TestCase):
    @patch("src.service.news_sentiment_service.NewsSentimentDAO")
    def setUp(self, MockNewsSentimentDAO):
        """Set up mock objects and test data."""
        self.mock_dao = MockNewsSentimentDAO.return_value
        self.service = NewsSentimentService()
        self.service.news_sentiment_dao = self.mock_dao

    def test_insert_sentiment(self):
        """Test the insert_sentiment method."""
        sentiment_data = {
            "trade_id": 1,
            "symbol": "AAPL",
            "sentiment_score": Decimal("0.75"),
            "headline": "Positive news about AAPL",
            "source": "Reuters",
            "published_at": datetime(2024, 4, 11, 14, 30, 0)
        }

        self.service.insert_sentiment(**sentiment_data)

        self.mock_dao.insert_sentiment.assert_called_once_with(
            1, "AAPL", Decimal("0.75"), "Positive news about AAPL", "Reuters", datetime(2024, 4, 11, 14, 30, 0)
        )
    
    def test_update_sentiment(self):
        """Test the update_sentiment method."""
        sentiment_data = {
            "sentiment_id": 1,
            "sentiment_score": Decimal("0.80"),
            "headline": "Updated news about AAPL",
            "source": "Bloomberg",
            "published_at": datetime(2024, 4, 12, 14, 30, 0)
        }

        self.service.update_sentiment(**sentiment_data)

        self.mock_dao.update_sentiment.assert_called_once_with(
            1, Decimal("0.80"), "Updated news about AAPL", "Bloomberg", datetime(2024, 4, 12, 14, 30, 0)
        )
    
    def test_delete_sentiment(self):
        """Test the delete_sentiment method."""
        sentiment_id = 1

        self.service.delete_sentiment(sentiment_id)

        self.mock_dao.delete_sentiment.assert_called_once_with(sentiment_id)
    
    def test_fetch_sentiment_by_trade_id(self):
        """Test the fetch_sentiment_by_trade_id method."""
        trade_id = 1
        sentiment_records = [
            (1, 1, "AAPL", Decimal("0.75"), "Positive news about AAPL", "Reuters", datetime(2024, 4, 11, 14, 30, 0)),
            (2, 1, "AAPL", Decimal("0.80"), "Updated news about AAPL", "Bloomberg", datetime(2024, 4, 12, 14, 30, 0))
        ]

        self.mock_dao.fetch_sentiment_by_trade_id.return_value = sentiment_records

        result = self.service.get_sentiment_by_trade_id(trade_id)

        self.mock_dao.fetch_sentiment_by_trade_id.assert_called_once_with(trade_id)
        self.assertEqual(result, sentiment_records)
            
    def test_fetch_sentiment_by_symbol(self):
        """Test the fetch_sentiment_by_symbol method."""
        symbol = "AAPL"
        sentiment_records = [
            (1, 1, "AAPL", Decimal("0.75"), "Positive news about AAPL", "Reuters", datetime(2024, 4, 11, 14, 30, 0)),
            (2, 1, "AAPL", Decimal("0.80"), "Updated news about AAPL", "Bloomberg", datetime(2024, 4, 12, 14, 30, 0))
        ]
        
        self.mock_dao.fetch_sentiment_by_symbol.return_value = sentiment_records
        
        result = self.service.get_sentiment_by_symbol(symbol)
        
        self.mock_dao.fetch_sentiment_by_symbol.assert_called_once_with(symbol)
        self.assertEqual(result, sentiment_records)
        
    def test_fetch_sentiment_by_symbol_and_date(self):
        """Test the fetch_sentiment_by_symbol_and_date method."""
        symbol = "AAPL"
        start_date = datetime(2024, 4, 1)
        end_date = datetime(2024, 4, 30)
        sentiment_records = [
            (1, 1, "AAPL", Decimal("0.75"), "Positive news about AAPL", "Reuters", datetime(2024, 4, 11, 14, 30, 0)),
            (2, 1, "AAPL", Decimal("0.80"), "Updated news about AAPL", "Bloomberg", datetime(2024, 4, 12, 14, 30, 0))
        ]
        
        self.mock_dao.fetch_sentiment_by_symbol_and_date.return_value = sentiment_records
        result = self.service.get_sentiment_by_symbol_and_date(symbol, start_date, end_date)
        self.mock_dao.fetch_sentiment_by_symbol_and_date.assert_called_once_with(symbol, start_date, end_date)
        self.assertEqual(result, sentiment_records)
        
    def tearDown(self):
        """Clean up mock objects."""
        self.mock_dao.reset_mock()
        self.service = None

if __name__ == "__main__":
    unittest.main()