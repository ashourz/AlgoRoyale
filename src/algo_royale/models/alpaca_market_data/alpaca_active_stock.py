# src/models/alpaca_models/alpaca_active_stock.py

from datetime import datetime
from typing import Optional

from dateutil.parser import isoparse  # if not using built-in parsing
from pydantic import BaseModel


class ActiveStock(BaseModel):
    """
    Represents a single active stock, containing information about its symbol, trade count, and volume.

    Attributes:
        symbol (str): The stock symbol.
        trade_count (int): The number of trades for the stock.
        volume (int): The trading volume for the stock.
    """

    symbol: str
    trade_count: int
    volume: int

    @staticmethod
    def from_raw(data: dict) -> "ActiveStock":
        """
        Convert raw data from Alpaca API response into an ActiveStock object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            ActiveStock: An ActiveStock object populated with values from the raw data.

        Example:
            data = {
                "symbol": "AAPL",
                "trade_count": 1000,
                "volume": 50000
            }
            active_stock = ActiveStock.from_raw(data)
        """
        return ActiveStock(
            symbol=data["symbol"],
            trade_count=data["trade_count"],
            volume=data["volume"],
        )


class MostActiveStocksResponse(BaseModel):
    """
    Represents a collection of the most active stocks.

    Attributes:
        last_updated (datetime): The timestamp when the data was last updated.
        most_actives (list[ActiveStock]): A list of the most active stocks.
    """

    last_updated: datetime
    most_actives: list[ActiveStock]

    @classmethod
    def from_raw(cls, data: dict) -> Optional["MostActiveStocksResponse"]:
        """
        Convert raw data from Alpaca API response into a MostActiveStocksResponse object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            MostActiveStocks: A MostActiveStocks object populated with values from the raw data.
        """
        return cls(
            last_updated=isoparse(data["last_updated"]),
            most_actives=[
                ActiveStock.from_raw(stock) for stock in data["most_actives"]
            ],
        )
