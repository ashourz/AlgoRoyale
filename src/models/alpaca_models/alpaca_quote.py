# src/models/alpaca_models/alpaca_quote.py

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse  # if not using built-in parsing


class Quote(BaseModel):
    """
    Represents a single stock quote, containing bid and ask information along with exchanges and conditions.

    Attributes:
        timestamp (datetime): The timestamp when the quote was taken.
        ask_exchange (str): The exchange where the ask price was listed.
        ask_price (float): The price at which the asset is being offered for sale (ask price).
        ask_size (int): The number of shares available at the ask price.
        bid_exchange (str): The exchange where the bid price was listed.
        bid_price (float): The price at which the asset is being offered to be bought (bid price).
        bid_size (int): The number of shares available at the bid price.
        conditions (List[str]): A list of conditions for the quote, such as `["P", "R"]` (e.g., "P" could represent "primary" exchange, and "R" might mean "retail").
        tape (str): The tape (market) where the transaction occurred (e.g., "A" for NYSE, "B" for Nasdaq).

    Methods:
        from_raw(data: dict) -> Quote:
            Converts raw dictionary data (from Alpaca API) into a Quote instance.
    """

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
    def from_raw(data: dict) -> "Quote":
        """
        Convert raw data from Alpaca API response into a Quote object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            Quote: A Quote object populated with values from the raw data.
        
        Example:
            data = {
                "t": "2024-04-01T00:00:00Z",
                "ax": "NYSE",
                "ap": 150.25,
                "as": 100,
                "bx": "NASDAQ",
                "bp": 150.00,
                "bs": 50,
                "c": ["P", "R"],
                "z": "A"
            }
            quote = Quote.from_raw(data)
        """
        return Quote(
            timestamp=isoparse(data["t"]),  # Timestamp of the quote
            ask_exchange=data["ax"],  # Ask exchange (where ask price is listed)
            ask_price=data["ap"],  # Ask price
            ask_size=data["as"],  # Ask size (number of shares available)
            bid_exchange=data["bx"],  # Bid exchange (where bid price is listed)
            bid_price=data["bp"],  # Bid price
            bid_size=data["bs"],  # Bid size (number of shares available)
            conditions=data["c"],  # Conditions (list of codes for conditions)
            tape=data["z"],  # Tape (market identifier)
        )


class QuotesResponse(BaseModel):
    """
    Represents the response from the Alpaca API when fetching historical stock quotes.
    
    Attributes:
        quotes (Dict[str, List[Quote]]): A dictionary where the keys are symbol tickers (e.g., "AAPL") and the values are lists of `Quote` objects for that symbol.
        next_page_token (Optional[str]): A token for pagination, used to fetch the next set of data if available. If there is no more data, this will be `None`.

    Example:
        response = {
            "quotes": {
                "AAPL": [
                    {"timestamp": "2024-04-01T00:00:00Z", "ask_exchange": "NYSE", "ask_price": 150.25, ...},
                    {"timestamp": "2024-04-01T00:01:00Z", "ask_exchange": "NASDAQ", "ask_price": 150.50, ...}
                ]
            },
            "next_page_token": "abcd1234"
        }
    """

    quotes: Dict[str, List[Quote]]  # Mapping of symbol (str) to list of Quote objects
    next_page_token: Optional[str]  # Token for pagination if more data is available
    
    @classmethod
    def from_raw(cls, data: dict) -> Optional["QuotesResponse"]:
        """
        Convert raw data from Alpaca API response into a QuotesResponse object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            QuotesResponse: A QuotesResponse object populated with values from the raw data.
        
        Example:
            response = {
                "quotes": {
                    "AAPL": [
                        {"timestamp": "2024-04-01T00:00:00Z", "ask_exchange": "NYSE", ...},
                        {"timestamp": "2024-04-01T00:01:00Z", "ask_exchange": "NASDAQ", ...}
                    ]
                },
                "next_page_token": "abcd1234"
            }
            quotes_response = QuotesResponse.from_raw(response)
        """
        if not data or "quotes" not in data:
            return None

        return cls(
            quotes={
                symbol: [Quote.from_raw(quote) for quote in quotes]
                for symbol, quotes in data.get("quotes", {}).items()
            },
            next_page_token=data.get("next_page_token")
        )
