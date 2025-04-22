from models.alpaca_trading.alpaca_asset import Asset
from pydantic import BaseModel, Field
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
    assets: List[Asset]

    class Config:
        orm_mode = True

    @staticmethod
    def from_raw(data: dict) -> "Watchlist":
        """
        Creates a Watchlist object from raw API data.

        Args:
            data (dict): A dictionary representing a watchlist from the Alpaca API.

        Returns:
            Watchlist: A Watchlist instance with structured fields.
        """
        return Watchlist(
            id=data["id"],
            account_id=data["account_id"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            name=data["name"],
            assets=[Asset.from_raw(asset) for asset in data.get("assets", [])],
        )
        
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