from datetime import datetime
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd
from dateutil.parser import isoparse  # If you want to use the isoparse method
from pydantic import BaseModel


def safe_float(val, default=np.nan):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


# Base model for a single historical price bar
# This is used to represent a single bar of market data for a stock symbol.
class Bar(BaseModel):
    """
    Represents a single historical price bar for a stock symbol.

    Attributes:
        timestamp (datetime): Time of the bar.
        open_price (float): Opening price.
        high_price (float): Highest price during the bar.
        low_price (float): Lowest price during the bar.
        close_price (float): Closing price.
        volume (int): Volume of shares traded.
        num_trades (int): Number of trades during the bar.
        volume_weighted_price (float): Volume-weighted average price.
    """

    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    num_trades: int
    volume_weighted_price: float

    @classmethod
    def parse_timestamp(
        cls, raw_ts: Union[int, str, pd.Timestamp, datetime]
    ) -> datetime:
        """Handle all supported timestamp formats."""
        if isinstance(raw_ts, (datetime, pd.Timestamp)):
            return (
                raw_ts
                if raw_ts.tzinfo is not None
                else raw_ts.replace(tzinfo=datetime.utc.tzinfo)
            )
        elif isinstance(raw_ts, int):
            return datetime.fromtimestamp(raw_ts, tz=datetime.utc.tzinfo)
        elif isinstance(raw_ts, str):
            return isoparse(raw_ts)
        raise ValueError(f"Unsupported timestamp type: {type(raw_ts)}")

    @classmethod
    def from_raw(cls, data: Union[dict, pd.Series]) -> "Bar":
        """Handle both Alpaca and DataFrame formats."""
        if isinstance(data, pd.Series):
            data = data.to_dict()

        # Extract timestamp
        timestamp = data.get("t") or data.get("timestamp")
        if timestamp is None:
            raise ValueError("Missing timestamp in data")

        return cls(
            timestamp=cls.parse_timestamp(timestamp),
            open_price=safe_float(
                data.get("o") or data.get("open_price") or data.get("open")
            ),
            high_price=safe_float(
                data.get("h") or data.get("high_price") or data.get("high")
            ),
            low_price=safe_float(
                data.get("l") or data.get("low_price") or data.get("low")
            ),
            close_price=safe_float(
                data.get("c") or data.get("close_price") or data.get("close")
            ),
            volume=safe_int(data.get("v") or data.get("volume")),
            num_trades=safe_int(data.get("n") or data.get("num_trades")),
            volume_weighted_price=safe_float(
                data.get("vw") or data.get("volume_weighted_price")
            ),
        )


class BarsResponse(BaseModel):
    """
    Represents a collection of historical bars for one or more stock symbols.

    Attributes:
        symbol_bars (Dict[str, list[Bar]]): A mapping from stock symbol to a list of Bar objects.
        next_page_token (Optional[str]): Token to fetch the next page of data, if available.
    """

    symbol_bars: Dict[str, list[Bar]]
    next_page_token: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_data: dict) -> "BarsResponse":
        """
                Creates a BarsResponse instance from raw API response.

                Args:
                    raw_data (dict): The raw dictionary response from the Alpaca API.

                Returns:

        def safe_float(val, default=np.nan):
            try:
                return float(val)
            except (TypeError, ValueError):
                return default

        def safe_int(val, default=0):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

                    BarsResponse: A parsed and validated BarsResponse object.
        """
        # We are expecting a "bars" dictionary containing symbols with their corresponding list of bars.
        parsed = {
            symbol: [Bar.from_raw(bar_data) for bar_data in bar_list]
            for symbol, bar_list in raw_data.get("bars", {}).items()
        }

        return cls(
            symbol_bars=parsed,
            next_page_token=raw_data.get(
                "next_page_token"
            ),  # You may need to add error handling if "next_page_token" is missing
        )


class LatestBarsResponse(BaseModel):
    """
    Represents the most recent market bar (price data) for one or more stock symbols.

    This model is used to parse the response from Alpaca's `/stocks/bars/latest` endpoint,
    which returns a single latest `Bar` object per requested symbol.

    Attributes:
        symbol_bars (Dict[str, Bar]): A mapping from stock symbol to its most recent Bar object.
    """

    symbol_bars: Dict[str, Bar]

    @classmethod
    def from_raw(cls, raw_data: dict) -> "LatestBarsResponse":
        """
        Creates a LatestBarsResponse instance from raw API response data.

        Args:
            raw_data (dict): The raw dictionary response from the Alpaca API.
                            Expected to contain a "bars" dictionary where each key
                            is a symbol and each value is a single bar (dict).

        Returns:
            LatestBarsResponse: A parsed and validated LatestBarsResponse object.
        """
        parsed = {
            symbol: Bar.from_raw(bar_data)
            for symbol, bar_data in raw_data.get("bars", {}).items()
        }
        return cls(symbol_bars=parsed)
