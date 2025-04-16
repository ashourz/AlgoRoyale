# src: tests/integration/client/test_alpaca_client.py

import logging
import asyncio
from models.alpaca_models.alpaca_quote import Quote, QuotesResponse
import pytest
from datetime import datetime, timezone
from algo_royale.client.alpaca_data_client import AlpacaDataClient

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaDataClient()

@pytest.mark.asyncio
class TestAlpacaDataClientIntegration:

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

