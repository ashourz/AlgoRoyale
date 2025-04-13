# src: tests/integration/client/test_alpaca_client.py

import logging
import asyncio
from models.alpaca_models.alpaca_quote import Quote, QuotesResponse
import pytest
from datetime import datetime, timezone
from alpaca.common.exceptions import APIError
from algo_royale.client.alpaca_data_client import AlpacaDataClient

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaDataClient()

@pytest.mark.asyncio
class TestAlpacaClientIntegration:

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

    def test_invalid_date(self, alpaca_client):
        """Test invalid date range handling."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 5)
        end_date = datetime(2024, 4, 1)

        with pytest.raises(APIError):
            alpaca_client.fetch_historical_data(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date
            )

    def test_no_data_for_symbol(self, alpaca_client):
        """Test fetching data for a symbol that has no historical data."""
        symbols = ["NONEXISTENT"]
        start_date = datetime(2024, 4, 1)
        end_date = datetime(2024, 4, 3)

        result = alpaca_client.fetch_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )

        assert result.empty or len(result) == 0

    def test_fetch_latest_quote(self, alpaca_client):
        """Test fetching the latest quote for a symbol."""
        quote = alpaca_client.fetch_latest_quote(
            symbol = "AAPL"
        )

        assert isinstance(quote, dict)
        assert "symbol" in quote
        assert quote["symbol"] == "AAPL"
        assert "timestamp" in quote
        assert isinstance(quote["timestamp"], datetime)
        assert "ask_price" in quote or "ap" in quote

    async def test_subscribe_and_receive_quote(self, alpaca_client):
        """Test subscribing to and receiving a quote from the quote stream."""
        received_quotes = []

        async def handler(quote):
            received_quotes.append(quote)
            await asyncio.sleep(0.1)
            alpaca_client.unsubscribe_quotes("AAPL")

        alpaca_client.subscribe_quotes(handler, "AAPL")

        await asyncio.sleep(5)

        assert len(received_quotes) > 0
        assert isinstance(received_quotes[0], dict)
        assert received_quotes[0].get("symbol") == "AAPL"
