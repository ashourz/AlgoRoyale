# src/models/alpaca_models/alpaca_trade.py

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse  # for parsing ISO 8601 formatted strings

class Trade(BaseModel):
    """
    Represents an individual trade in the Alpaca historical trades data.
    
    Attributes:
        timestamp (datetime): The timestamp of the trade.
        exchange (str): The exchange where the trade occurred.
        price (float): The price of the trade.
        size (int): The size of the trade (number of shares).
        conditions (List[str]): A list of conditions associated with the trade.
        identifier (int): The unique identifier for the trade.
        trade_type (str): The type of the trade (e.g., 'C' for regular, 'I' for auction).
    """
    
    timestamp: datetime
    exchange: str
    price: float
    size: int
    conditions: List[str]
    identifier: int
    trade_type: str

    @staticmethod
    def from_raw(data: dict) -> "Trade":
        """
        Convert raw data from Alpaca API response into a Trade object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            Trade: A Trade object populated with values from the raw data.
        """
        return Trade(
            timestamp=isoparse(data["t"]),
            exchange=data["x"],
            price=data["p"],
            size=data["s"],
            conditions=data["c"],
            identifier=data["i"],
            trade_type=data["z"]
        )

class HistoricalTradesResponse(BaseModel):
    """
    Represents the response from the Alpaca API when fetching historical trades data.
    
    Attributes:
        trades (Dict[str, List[Trade]]): A dictionary where keys are stock symbols (e.g., 'AAPL')
            and values are lists of trades for each symbol.
        next_page_token (Optional[str]): Token for pagination if more data is available.
    """
    
    trades: Dict[str, List[Trade]]
    next_page_token: Optional[str]  # Token for pagination

    @classmethod
    def from_raw(cls, data: dict) -> "HistoricalTradesResponse":
        """
        Convert raw data from Alpaca API response into a HistoricalTradesResponse object.
        
        Args:
            data (dict): The raw data returned from Alpaca API.
            
        Returns:
            HistoricalTradesResponse: A HistoricalTradesResponse object populated with values from the raw data.
        """
        
        if not data or "trades" not in data:
            return None
        
        return cls(
            trades={symbol: [Trade.from_raw(trade) for trade in trades] 
                    for symbol, trades in data["trades"].items()},
            next_page_token=data.get("next_page_token")
        )
