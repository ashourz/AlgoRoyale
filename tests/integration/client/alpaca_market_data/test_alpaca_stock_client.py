# src: tests/integration/client/test_alpaca_client.py

import pytest
from datetime import datetime, timezone
from shared.models.alpaca_market_data.alpaca_auction import AuctionResponse
from shared.models.alpaca_market_data.alpaca_bar import Bar, BarsResponse, LatestBarsResponse
from shared.models.alpaca_market_data.alpaca_condition_code import ConditionCodeMap
from shared.models.alpaca_market_data.alpaca_quote import Quote, QuotesResponse
from shared.models.alpaca_market_data.alpaca_snapshot import SnapshotsResponse
from shared.models.alpaca_market_data.alpaca_trade import HistoricalTradesResponse, LatestTradesResponse, Trade
from the_risk_is_not_enough.client.alpaca_market_data.alpaca_stock_client import AlpacaStockClient, Tape, TickType

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()


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

    def test_fetch_historical_bars(self, alpaca_client):
        """Test fetching historical bars for a symbol."""
        symbols = ["AAPL"]
        start_date = datetime(2022, 1, 3, tzinfo=timezone.utc)
        end_date = datetime(2022, 1, 4, tzinfo=timezone.utc)

        result = alpaca_client.fetch_historical_bars(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )

        # Basic assertions
        assert result is not None
        assert isinstance(result, BarsResponse)

        # Verify bar structure for each symbol
        for symbol in symbols:
            bars = result.symbol_bars.get(symbol)
            assert bars is not None
            assert isinstance(bars, list)

            for bar in bars:
                assert hasattr(bar, "timestamp")
                assert hasattr(bar, "open_price")
                assert hasattr(bar, "high_price")
                assert hasattr(bar, "low_price")
                assert hasattr(bar, "close_price")
                assert hasattr(bar, "volume")
                assert hasattr(bar, "num_trades")
                assert hasattr(bar, "volume_weighted_price")

                assert isinstance(bar.timestamp, datetime)
                assert bar.open_price > 0
                assert bar.high_price >= bar.low_price
                assert bar.volume >= 0
                assert bar.num_trades >= 0
                
    def test_fetch_latest_bars(self, alpaca_client):
        """Test fetching latest bars for a symbol."""
        symbols = ["AAPL"]
        start_date = datetime(2022, 1, 3, tzinfo=timezone.utc)
        end_date = datetime(2022, 1, 4, tzinfo=timezone.utc)

        result = alpaca_client.fetch_latest_bars(
            symbols=symbols
        )

        # Basic assertions
        assert result is not None
        assert isinstance(result, LatestBarsResponse)

        # Verify bar structure for each symbol
        for symbol in symbols:
            bar = result.symbol_bars.get(symbol)
            assert bar is not None
            assert isinstance(bar, Bar)

            assert hasattr(bar, "timestamp")
            assert hasattr(bar, "open_price")
            assert hasattr(bar, "high_price")
            assert hasattr(bar, "low_price")
            assert hasattr(bar, "close_price")
            assert hasattr(bar, "volume")
            assert hasattr(bar, "num_trades")
            assert hasattr(bar, "volume_weighted_price")

            assert isinstance(bar.timestamp, datetime)
            assert bar.open_price > 0
            assert bar.high_price >= bar.low_price
            assert bar.volume >= 0
            assert bar.num_trades >= 0
            
    def test_fetch_condition_codes(self, alpaca_client):
        """Test fetching condition codes from Alpaca."""

        # Example test inputs
        ticktype = TickType.TRADE  # or use TickType.TRADE if it's an enum
        tape = Tape.A          # or use Tape.A

        # Call the method
        result = alpaca_client.fetch_condition_codes(
            ticktype=ticktype,
            tape=tape
        )

        # Basic assertions
        assert result is not None
        assert isinstance(result, ConditionCodeMap)

        # Validate the internal dictionary
        condition_dict = result.root
        assert isinstance(condition_dict, dict)
        assert len(condition_dict) > 0  # should contain at least one mapping

        # Check a known condition code (if mocking, include this one in mock data)
        for key, value in condition_dict.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) == 1  # condition code should be one character
            assert len(value) > 0  # description should be non-empty

        # Test the describe method on an actual key
        first_key = next(iter(condition_dict))
        description = result.describe(first_key)
        assert description == condition_dict[first_key]
        
    def test_fetch_snapshots(self, alpaca_client):
        """Test fetching snapshot data from Alpaca."""

        # Example test input
        symbols = ["AAPL"]

        # Call the method
        result = alpaca_client.fetch_snapshots(
            symbols=symbols
        )

        # Basic assertions
        assert result is not None
        assert isinstance(result, SnapshotsResponse)

        # Validate internal structure
        snapshot_dict = result.root
        assert isinstance(snapshot_dict, dict)
        assert "AAPL" in snapshot_dict

        snapshot = snapshot_dict["AAPL"]
        assert snapshot is not None

        # Latest Trade
        if hasattr(snapshot, 'latest_trade') and snapshot.latest_trade:
            trade = snapshot.latest_trade
            assert trade.price is not None
            assert trade.size >= 0
            assert isinstance(trade.price, float)

        # Latest Quote
        if hasattr(snapshot, 'latest_quote') and snapshot.latest_quote:
            quote = snapshot.latest_quote
            assert quote.ask_price >= 0
            assert quote.bid_price >= 0
            assert isinstance(quote.ask_price, float)

        # Minute Bar
        if hasattr(snapshot, 'minute_bar') and snapshot.minute_bar:
            bar = snapshot.minute_bar
            assert bar.open_price is not None
            assert bar.close_price is not None
            assert isinstance(bar.volume, int)

        # Daily Bar
        if hasattr(snapshot, 'daily_bar') and snapshot.daily_bar:
            daily = snapshot.daily_bar
            assert daily.high_price >= daily.low_price
            assert isinstance(daily.volume, int)

        # Previous Daily Bar
        if hasattr(snapshot, 'prev_daily_bar') and snapshot.prev_daily_bar:
            prev_daily = snapshot.prev_daily_bar
            assert prev_daily.high_price >= prev_daily.low_price
            assert isinstance(prev_daily.volume, int)
    

        # Optional: print output for debugging or manual verification
        # print(snapshot.model_dump_json(indent=2))

    def test_fetch_historical_trades(self, alpaca_client):
        """Test fetching historical trades for a symbol."""
        symbols = ["AAPL"]
        start_date = datetime(2022, 1, 3, tzinfo=timezone.utc)
        end_date = datetime(2022, 1, 4, tzinfo=timezone.utc)

        result = alpaca_client.fetch_historical_trades(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )

        # Inspect the actual response
        print(result)  # Add this line to print the response from Alpaca

        # Basic assertions
        assert result is not None
        assert isinstance(result, HistoricalTradesResponse)

        # Verify trade structure for each symbol
        for symbol in symbols:
            trades = result.trades.get(symbol)
            assert trades is not None
            assert isinstance(trades, list)
            for trade in trades:
                assert isinstance(trade, Trade)
                assert hasattr(trade, "timestamp")
                assert hasattr(trade, "exchange")
                assert hasattr(trade, "price")
                assert hasattr(trade, "size")
                assert hasattr(trade, "conditions")
                assert hasattr(trade, "identifier")
                assert hasattr(trade, "trade_type")

                # Ensure the trade attributes are of the correct type and values are reasonable
                assert isinstance(trade.timestamp, datetime)
                assert isinstance(trade.price, float)
                assert trade.price > 0
                assert isinstance(trade.size, int)
                assert trade.size >= 0
                
    def test_fetch_latest_trades(self, alpaca_client):
        """Test fetching latest trades for a symbol."""
        symbols = ["AAPL"]

        result = alpaca_client.fetch_latest_trades(
            symbols=symbols
        )

        # Inspect the actual response
        print(result)  # Add this line to print the response from Alpaca

        # Basic assertions
        assert result is not None
        assert isinstance(result, LatestTradesResponse)

        # Verify trade structure for each symbol
        for symbol in symbols:
            trade = result.trades.get(symbol)
   
            assert isinstance(trade, Trade)
            assert hasattr(trade, "timestamp")
            assert hasattr(trade, "exchange")
            assert hasattr(trade, "price")
            assert hasattr(trade, "size")
            assert hasattr(trade, "conditions")
            assert hasattr(trade, "identifier")
            assert hasattr(trade, "trade_type")

            # Ensure the trade attributes are of the correct type and values are reasonable
            assert isinstance(trade.timestamp, datetime)
            assert isinstance(trade.price, float)
            assert trade.price > 0
            assert isinstance(trade.size, int)
            assert trade.size >= 0