from models.alpaca_trading.alpaca_asset import Asset
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Watchlist(BaseModel):
    """
    Represents a watchlist entry from the Alpaca API, with associated assets.

    Attributes:
        id (str): Unique identifier for the watchlist.
        account_id (str): The associated account's ID.
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.
        name (str): The name of the watchlist.
        assets (List[Asset]): List of assets in the watchlist.
    """
    id: str
    account_id: str
    created_at: datetime
    updated_at: datetime
    name: str
    assets: Optional[List[Asset]] = []

    class Config:
        orm_mode = True

    @classmethod
    def from_raw(cls, data: dict) -> "Watchlist":
        """
        Factory method to convert raw API data into a structured Watchlist object.
        Converts date strings to datetime and maps asset entries.
        """
        for field in ['created_at', 'updated_at']:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))

        if 'assets' in data and isinstance(data['assets'], list):
            data['assets'] = [Asset(**asset) for asset in data['assets']]

        return cls(**data)

class WatchlistListResponse(BaseModel):
    """
    Represents a list of Watchlist objects returned from the Alpaca API.
    """

    watchlists: List[Watchlist]

    @classmethod
    def from_raw(cls, data: List[dict]) -> "WatchlistListResponse":
        """
        Factory method to parse a raw list of watchlist dictionaries
        into structured Watchlist objects.
        """
        parsed_watchlists = [Watchlist.from_raw(item) for item in data]
        return cls(watchlists=parsed_watchlists)