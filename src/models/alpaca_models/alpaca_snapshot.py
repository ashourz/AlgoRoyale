# src/models/alpaca_models/alpaca_snapshot.py

from pydantic import BaseModel, Field, RootModel
from typing import Dict, List, Optional


class Trade(BaseModel):
    """
    Represents a trade event for a stock.

    Attributes:
        timestamp: ISO 8601 timestamp of the trade.
        exchange: Exchange where the trade occurred.
        price: Trade price.
        size: Trade size (number of shares).
        conditions: List of condition codes.
        trade_id: Unique identifier for the trade.
        tape: The SIP tape (A, B, or C) the trade came from.
    """
    timestamp: str = Field(..., alias="t", description="ISO 8601 timestamp of the trade")
    exchange: str = Field(..., alias="x", description="Exchange where the trade occurred")
    price: float = Field(..., alias="p", description="Trade price")
    size: int = Field(..., alias="s", description="Trade size in shares")
    conditions: List[str] = Field(..., alias="c", description="List of condition codes")
    trade_id: int = Field(..., alias="i", description="Unique identifier for the trade")
    tape: str = Field(..., alias="z", description="SIP tape the trade came from (A, B, or C)")

    @classmethod
    def from_raw(cls, raw: dict) -> "Trade":
        """Parses raw Alpaca trade data into a Trade model."""
        return cls.model_validate(raw)


class Quote(BaseModel):
    """
    Represents a quote event for a stock.

    Attributes:
        timestamp: ISO 8601 timestamp of the quote.
        ask_exchange: Exchange posting the ask price.
        ask_price: Current ask price.
        ask_size: Number of shares available at ask.
        bid_exchange: Exchange posting the bid price.
        bid_price: Current bid price.
        bid_size: Number of shares available at bid.
        conditions: List of condition codes.
        tape: The SIP tape the quote came from.
    """
    timestamp: str = Field(..., alias="t", description="ISO 8601 timestamp of the quote")
    ask_exchange: str = Field(..., alias="ax", description="Exchange for the ask price")
    ask_price: float = Field(..., alias="ap", description="Current ask price")
    ask_size: int = Field(..., alias="as", description="Size at ask price")
    bid_exchange: str = Field(..., alias="bx", description="Exchange for the bid price")
    bid_price: float = Field(..., alias="bp", description="Current bid price")
    bid_size: int = Field(..., alias="bs", description="Size at bid price")
    conditions: List[str] = Field(..., alias="c", description="List of condition codes")
    tape: str = Field(..., alias="z", description="SIP tape the quote came from")

    @classmethod
    def from_raw(cls, raw: dict) -> "Quote":
        """Parses raw Alpaca quote data into a Quote model."""
        return cls.model_validate(raw)


class Bar(BaseModel):
    """
    Represents a bar (candlestick) for a given time period.

    Attributes:
        timestamp: ISO 8601 timestamp of the bar.
        open_price: Opening price.
        high_price: Highest price.
        low_price: Lowest price.
        close_price: Closing price.
        volume: Total volume traded.
        trade_count: Number of trades in this interval.
        vwap: Volume-weighted average price.
    """
    timestamp: str = Field(..., alias="t", description="ISO 8601 timestamp for the bar")
    open_price: float = Field(..., alias="o", description="Opening price")
    high_price: float = Field(..., alias="h", description="Highest price")
    low_price: float = Field(..., alias="l", description="Lowest price")
    close_price: float = Field(..., alias="c", description="Closing price")
    volume: int = Field(..., alias="v", description="Total volume traded")
    trade_count: int = Field(..., alias="n", description="Number of trades in interval")
    vwap: float = Field(..., alias="vw", description="Volume-weighted average price")

    @classmethod
    def from_raw(cls, raw: dict) -> "Bar":
        """Parses raw Alpaca bar data into a Bar model."""
        return cls.model_validate(raw)


class Snapshot(BaseModel):
    """
    Represents a snapshot of recent trading activity for a single symbol.

    Attributes:
        latest_trade: The most recent trade data.
        latest_quote: The most recent quote data.
        minute_bar: Bar for the current minute.
        daily_bar: Today's trading bar.
        previous_daily_bar: Yesterday's trading bar (optional).
    """
    latest_trade: Optional[Trade]  # Make this field optional
    latest_quote: Optional[Quote]  # Make this field optional
    minute_bar: Optional[Bar]  # Make this field optional
    daily_bar: Optional[Bar]  # Make this field optional
    previous_daily_bar: Optional[Bar]  # Make this field optional

    @classmethod
    def from_raw(cls, raw: dict) -> "Snapshot":
        """Parses raw snapshot data into a Snapshot model."""
        return cls(
            latest_trade=Trade.from_raw(raw["latestTrade"]) if "latestTrade" in raw else None,
            latest_quote=Quote.from_raw(raw["latestQuote"]) if "latestQuote" in raw else None,
            minute_bar=Bar.from_raw(raw["minuteBar"]) if "minuteBar" in raw else None,
            daily_bar=Bar.from_raw(raw["dailyBar"]) if "dailyBar" in raw else None,
            previous_daily_bar=Bar.from_raw(raw["prevDailyBar"]) if "prevDailyBar" in raw else None,
        )


class SnapshotsResponse(RootModel[Dict[str, Snapshot]]):
    """
    Maps stock symbols to their snapshot data.

    Example:
        {
            "AAPL": Snapshot(...),
            "TSLA": Snapshot(...)
        }
    """
    @classmethod
    def from_raw(cls, raw: dict) -> "SnapshotsResponse":
        """Parses the entire snapshots response into a dictionary of Snapshots."""
        return cls({
            symbol: Snapshot.from_raw(data)
            for symbol, data in raw.items()
        })
