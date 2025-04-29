# src/models/alpaca_models/alpaca_active_stock.py

from pydantic import BaseModel, RootModel
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse  # if not using built-in parsing

class AuctionEvent(BaseModel):
    condition: str         # e.g. "M", "6", "Q", "O"
    price: float           # e.g. 182.01
    size: int              # number of shares
    timestamp: datetime    # e.g. "2022-01-03T21:00:00.121043712Z"
    exchange_code: str     # e.g. "P", "T", "Q"

    @staticmethod
    def from_raw(data: dict) -> "AuctionEvent":
        return AuctionEvent(
            condition=data["c"],
            price=data["p"],
            size=data["s"],
            timestamp=data["t"],
            exchange_code=data["x"],
        )


class AuctionDay(BaseModel):
    date: str                          # e.g. "2022-01-03"
    closing_events: List[AuctionEvent]
    opening_events: List[AuctionEvent]

    @classmethod
    def from_raw(cls, data: dict) -> "AuctionDay":
        return cls(
            date=data["d"],
            closing_events=[AuctionEvent.from_raw(event) for event in data["c"]],
            opening_events=[AuctionEvent.from_raw(event) for event in data["o"]],
        )



class Auctions(RootModel[dict[str, list[AuctionDay]]]):
    """Represents a mapping of symbols to lists of auction data per day."""

    @classmethod
    def from_raw(cls, raw_data: dict) -> "Auctions":
        """
        Parse raw API response data into the Auctions model.

        Args:
            raw_data (dict): The raw dictionary from the API.

        Returns:
            Auctions: A parsed Auctions model instance.
        """
        parsed = {
            symbol: [AuctionDay.from_raw(day) for day in day_list]
            for symbol, day_list in raw_data.items()
        }
        return cls(root=parsed)
    
    def get_by_symbol(self, symbol: str) -> List[AuctionDay]:
        """
        Fetch auction data for a given symbol.

        Args:
            symbol (str): The stock symbol to look up.

        Returns:
            List[AuctionDay]: The list of auction data for the symbol, or an empty list if not found.
        """
        return self.root.get(symbol, [])


class AuctionResponse(BaseModel):
    auctions: Auctions
    next_page_token: Optional[str] = None

    @classmethod
    def from_raw(cls, data: dict) -> "AuctionResponse":
        return cls(
            auctions=Auctions.from_raw(data["auctions"]),
            next_page_token=data.get("next_page_token"),
        )