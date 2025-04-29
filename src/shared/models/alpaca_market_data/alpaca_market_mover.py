# src/models/alpaca_models/alpaca_corporate_action.py

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse  # if not using built-in parsing

class MarketMover(BaseModel):
    """
    Represents a single market mover, containing information about its symbol, trade count, and volume.
    
    Attributes:
        symbol (str): The stock symbol.
        trade_count (int): The number of trades for the stock.
        volume (int): The trading volume for the stock.
    """
    change: float
    percent_change: float
    price: float
    symbol: str
    
    @staticmethod
    def from_raw(data: dict) -> "MarketMover":
        """
        Convert raw data from Alpaca API response into a MarketMover object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            MarketMover: A MarketMover object populated with values from the raw data.
            
        Example:
            data = {
                "symbol": "AAPL",
                "trade_count": 1000,
                "volume": 50000
            }
            market_mover = MarketMover.from_raw(data)
        """
        return MarketMover(
            change=data["change"],
            percent_change=data["percent_change"],
            price=data["price"],
            symbol=data["symbol"]
        )

class MarketMoversResponse(BaseModel):
    """
    Represents a collection of market movers.
    
    Attributes:
        market_type (str): The type of market (e.g., "gainers", "losers").
        last_updated (datetime): The timestamp when the data was last updated.
        gainers (List[MarketMover]): A list of gainers.
        losers (List[MarketMover]): A list of losers.
    """
    market_type: str
    last_updated: datetime
    gainers: List[MarketMover]
    losers: List[MarketMover]
    
    @classmethod
    def from_raw(cls, data: dict) -> "MarketMoversResponse":
        """
        Convert raw data from Alpaca API response into a MarketMoversResponse object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            MarketMoversResponse: A MarketMoversResponse object populated with values from the raw data.
            
        Example:
            data = {
                "market_type": "gainers",
                "last_updated": "2024-04-01T00:00:00Z",
                "gainers": [
                    {
                        "symbol": "AAPL",
                        "trade_count": 1000,
                        "volume": 50000
                    }
                ],
                "losers": [
                    {
                        "symbol": "TSLA",
                        "trade_count": 800,
                        "volume": 30000
                    }
                ]
            }
            market_movers_response = MarketMoversResponse.from_raw(data)
        """
        return cls(
            market_type=data["market_type"],
            last_updated=isoparse(data["last_updated"]),
            gainers=[MarketMover.from_raw(item) for item in data["gainers"]],
            losers=[MarketMover.from_raw(item) for item in data["losers"]]
        )