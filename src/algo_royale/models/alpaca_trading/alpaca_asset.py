# src/models/alpaca_models/alpaca_asset.py

from typing import List
from pydantic import BaseModel


class Asset(BaseModel):
    """
    Represents a financial asset returned by the Alpaca Assets API.

    Attributes:
        id (str): Unique identifier for the asset.
        class_ (str): Asset class (e.g., 'us_equity').
        exchange (str): The exchange the asset is traded on (e.g., 'NASDAQ').
        symbol (str): The trading symbol (e.g., 'AAPL').
        name (str): Full name or description of the asset.
        status (str): Current status of the asset (e.g., 'active', 'inactive').
        tradable (bool): Whether the asset is currently tradable.
        marginable (bool): Whether the asset is eligible for margin trading.
        maintenance_margin_requirement (int): Margin maintenance requirement in percentage.
        shortable (bool): Whether the asset can be sold short.
        easy_to_borrow (bool): Indicates if the asset is easy to borrow for shorting.
        fractionable (bool): Whether the asset supports fractional share trading.
        attributes (List[str]): Additional asset-specific attributes (if any).
    """

    id: str
    class_: str  # Renamed from 'class' since it's a reserved keyword in Python
    exchange: str
    symbol: str
    name: str
    status: str
    tradable: bool
    marginable: bool
    maintenance_margin_requirement: int
    shortable: bool
    easy_to_borrow: bool
    fractionable: bool
    attributes: List[str]

    @staticmethod
    def from_raw(data: dict) -> "Asset":
        """
        Creates an Asset object from raw API data.

        Args:
            data (dict): A dictionary representing a single asset from the Alpaca API.

        Returns:
            Asset: An Asset instance with populated fields from the API response.
        """
        return Asset(
            id=data["id"],
            class_=data["class"],
            exchange=data["exchange"],
            symbol=data["symbol"],
            name=data["name"],
            status=data["status"],
            tradable=data["tradable"],
            marginable=data["marginable"],
            maintenance_margin_requirement=data["maintenance_margin_requirement"],
            shortable=data["shortable"],
            easy_to_borrow=data["easy_to_borrow"],
            fractionable=data["fractionable"],
            attributes=data.get("attributes") or []
        )

    def parse_assets(raw_data: List[dict]) -> List["Asset"]:
        """
        Parses a list of raw asset dictionaries into a list of Asset model instances.

        Args:
            raw_data (List[dict]): List of dictionaries, each representing an asset.

        Returns:
            List[Asset]: A list of Asset model instances.
        """
        return [Asset.from_raw(asset) for asset in raw_data]