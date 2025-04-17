# src/models/alpaca_models/alpaca_active_stock.py

from pydantic import BaseModel, RootModel
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse  # if not using built-in parsing

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


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
    def from_raw(cls, data: dict) -> "Bar":
        """Create a Bar instance from raw dictionary data (Alpaca format)."""
        return cls(
            timestamp=data["t"],
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
        Creates a Bars instance from raw API response.

        Args:
            raw_data (dict): The raw dictionary response from the Alpaca API.

        Returns:
            Bars: A parsed and validated Bars object.
        """
        parsed = {
            symbol: [Bar.from_raw(bar_data) for bar_data in bar_list]
            for symbol, bar_list in raw_data.get("bars", {}).items()
        }
        return cls(
            symbol_bars=parsed,
            next_page_token=raw_data.get("next_page_token")
        )
