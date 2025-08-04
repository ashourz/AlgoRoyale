from datetime import datetime
from typing import List

from dateutil.parser import isoparse
from pydantic import BaseModel


class StreamQuote(BaseModel):
    """
    Represents a streaming stock quote update received via Alpaca's WebSocket.

    Attributes:
        symbol (str): The ticker symbol of the asset.
        timestamp (datetime): Timestamp of the quote.
        ask_exchange (str): Exchange code for the ask.
        ask_price (float): Ask price. Market buy orders will use this price. Limit buy orders will use this price or lower.
        ask_size (int): Ask size. Market buy orders will use this size. Limit buy orders will use this size or lower.
        bid_exchange (str): Exchange code for the bid.
        bid_price (float): Bid price. Market sell orders will use this price. Limit sell orders will use this price or higher.
        bid_size (int): Bid size. Market sell orders will use this size. Limit sell orders will use this size or higher.
        conditions (list[str]): Quote condition codes.
        tape (str): Market tape identifier.
    """

    symbol: str
    timestamp: datetime
    ask_exchange: str
    ask_price: float
    ask_size: int
    bid_exchange: str
    bid_price: float
    bid_size: int
    conditions: List[str]
    tape: str

    @staticmethod
    def from_raw(data: dict) -> "StreamQuote":
        """
        Convert raw WebSocket message from Alpaca into a StreamQuote instance.

        Args:
            data (dict): Raw streaming quote dictionary from Alpaca.

        Returns:
            StreamQuote: Parsed quote model.
        """
        return StreamQuote(
            symbol=data["S"],
            timestamp=isoparse(data["t"]),
            ask_exchange=data["ax"],
            ask_price=data["ap"],
            ask_size=data["as"],
            bid_exchange=data["bx"],
            bid_price=data["bp"],
            bid_size=data["bs"],
            conditions=data["c"],
            tape=data["z"],
        )
