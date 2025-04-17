# src: tests/integration/client/test_alpaca_client.py

import logging
import asyncio
from models.alpaca_models.alpaca_auction import AuctionResponse
from models.alpaca_models.alpaca_quote import Quote, QuotesResponse
import pytest
from datetime import datetime, timezone
from algo_royale.client.alpaca_stock_client import AlpacaStockClient

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaStockClient()

@pytest.mark.asyncio
class TestAlpacaStockClientIntegration:

    def test_fetch_historical_quotes(self, alpaca_client):
        """Test fetching historical quote data from Alpaca's live endpoint."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = alpaca_client.fetch_historical_quotes(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )

        assert result is not None
        assert isinstance(result, QuotesResponse)
        assert "AAPL" in result.quotes
        assert len(result.quotes["AAPL"]) > 0

        first_quote = result.quotes["AAPL"][0]
        assert isinstance(first_quote, Quote)

        expected_attrs = [
            "timestamp", "ask_exchange", "ask_price", "ask_size",
            "bid_exchange", "bid_price", "bid_size", "conditions", "tape"
        ]
        for attr in expected_attrs:
            assert hasattr(first_quote, attr), f"Missing expected attribute: {attr}"
            
    def test_fetch_latest_quotes(self, alpaca_client):
        """Test fetching the latest quote for a symbol."""
        symbols = ["AAPL"]

        result = alpaca_client.fetch_latest_quotes(
            symbols=symbols
        )

        assert result is not None
        assert isinstance(result, QuotesResponse)
        assert "AAPL" in result.quotes
        assert len(result.quotes["AAPL"]) > 0

        first_quote = result.quotes["AAPL"][0]
        assert isinstance(first_quote, Quote)

        expected_attrs = [
            "timestamp", "ask_exchange", "ask_price", "ask_size",
            "bid_exchange", "bid_price", "bid_size", "conditions", "tape"
        ]
        for attr in expected_attrs:
            assert hasattr(first_quote, attr), f"Missing expected attribute: {attr}"
            
                        
    def test_fetch_historical_auctions(self, alpaca_client):
        """Test fetching the latest quote for a symbol."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)
        
        result = alpaca_client.fetch_historical_auctions(
            symbols=symbols,
            start_date = start_date,
            end_date = end_date
        )

        # Basic assertions
        assert result is not None
        assert isinstance(result, AuctionResponse)

        # Verify auction structure for each symbol
        for symbol in symbols:
            auction_days = result.auctions.get_by_symbol(symbol)
            assert auction_days is not None
            assert isinstance(auction_days, list)

            for day in auction_days:
                assert hasattr(day, "date")
                assert hasattr(day, "opening_events")
                assert hasattr(day, "closing_events")
                assert isinstance(day.opening_events, list)
                assert isinstance(day.closing_events, list)

                for event in day.opening_events + day.closing_events:
                    assert event.price > 0
                    assert event.size >= 0
                    assert isinstance(event.timestamp, datetime)
