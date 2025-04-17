# src/models/alpaca_models/alpaca_bar.py

from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from datetime import datetime
from dateutil.parser import isoparse  # If you want to use the isoparse method

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
    def parse_timestamp(cls, raw_ts: Union[int, str]) -> datetime:
        """Parses a timestamp from int (Unix) or ISO string."""
        if isinstance(raw_ts, int):
            return datetime.fromtimestamp(raw_ts, tz=datetime.utc.tzinfo)
        elif isinstance(raw_ts, str):
            return isoparse(raw_ts)
        raise ValueError(f"Unsupported timestamp type: {type(raw_ts)}")
    
    @classmethod
    def from_raw(cls, data: dict) -> "Bar":
        """Create a Bar instance from raw dictionary data (Alpaca format)."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict but got {type(data)}: {data}")
        
        return cls(
            timestamp=cls.parse_timestamp(data["t"]),
            open_price=data["o"],
            high_price=data["h"],
            low_price=data["l"],
            close_price=data["c"],
            volume=data["v"],
            num_trades=data["n"],
            volume_weighted_price=data["vw"],
        )


class BarsResponse(BaseModel):
    """
    Represents a collection of historical bars for one or more stock symbols.

    Attributes:
        symbol_bars (Dict[str, List[Bar]]): A mapping from stock symbol to a list of Bar objects.
        next_page_token (Optional[str]): Token to fetch the next page of data, if available.
    """
    symbol_bars: Dict[str, List[Bar]]
    next_page_token: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_data: dict) -> "BarsResponse":
        """
        Creates a BarsResponse instance from raw API response.

        Args:
            raw_data (dict): The raw dictionary response from the Alpaca API.

        Returns:
            BarsResponse: A parsed and validated BarsResponse object.
        """
        # We are expecting a "bars" dictionary containing symbols with their corresponding list of bars.
        parsed = {
            symbol: [Bar.from_raw(bar_data) for bar_data in bar_list]
            for symbol, bar_list in raw_data.get("bars", {}).items()
        }
        
        return cls(
            symbol_bars=parsed,
            next_page_token=raw_data.get("next_page_token")  # You may need to add error handling if "next_page_token" is missing
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