# src/models/alpaca_models/alpaca_trading/alpaca_order.py

from algo_royale.models.alpaca_trading.alpaca_order import Order
from pydantic import BaseModel
from typing import List
from enum import Enum


class PositionSide(str, Enum):
    long = "long"
    short = "short"


class Position(BaseModel):
    """
    Represents an open position in an Alpaca account.

    Attributes:
        asset_id (str): Unique identifier for the asset.
        symbol (str): The trading symbol of the asset.
        exchange (str): The exchange where the asset is traded.
        asset_class (str): The class of the asset (e.g., "us_equity").
        asset_marginable (bool): Whether the asset is marginable.
        qty (float): Total quantity of the position.
        qty_available (float): Quantity of the position available for trading.
        avg_entry_price (float): The average price at which the position was entered.
        side (PositionSide): Indicates whether the position is long or short.
        market_value (float): Current market value of the position.
        cost_basis (float): Total cost basis of the position.
        unrealized_pl (float): Total unrealized profit/loss.
        unrealized_plpc (float): Unrealized profit/loss as a percentage.
        unrealized_intraday_pl (float): Unrealized intraday profit/loss.
        unrealized_intraday_plpc (float): Intraday P/L as a percentage.
        current_price (float): The current price of the asset.
        lastday_price (float): The closing price of the asset from the previous trading day.
        change_today (float): The percent change in price from the previous day.
    """

    asset_id: str
    symbol: str
    exchange: str
    asset_class: str
    asset_marginable: bool

    qty: float
    qty_available: float
    avg_entry_price: float

    side: PositionSide

    market_value: float
    cost_basis: float

    unrealized_pl: float
    unrealized_plpc: float
    unrealized_intraday_pl: float
    unrealized_intraday_plpc: float

    current_price: float
    lastday_price: float
    change_today: float

    class Config:
        orm_mode = True

    @classmethod
    def from_raw(cls, data: dict) -> "Position":
        """
        Factory method to convert raw API data into a structured Position object.
        Handles float conversion and enum mapping.
        """
        float_fields = [
            "qty", "qty_available", "avg_entry_price", "market_value", "cost_basis",
            "unrealized_pl", "unrealized_plpc", "unrealized_intraday_pl", "unrealized_intraday_plpc",
            "current_price", "lastday_price", "change_today"
        ]

        for field in float_fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (TypeError, ValueError):
                    pass  # Leave original if conversion fails

        if "side" in data and isinstance(data["side"], str):
            try:
                data["side"] = PositionSide(data["side"])
            except ValueError:
                pass  # Leave as-is if it's not a recognized enum value

        return cls(**data)


class PositionList(BaseModel):
    """
    Represents a list of OrderResponse objects returned from the Alpaca API.
    """

    positions: List[Position]

    @classmethod
    def from_raw(cls, data: List[dict]) -> "PositionList":
        """
        Factory method to parse a raw list of order dictionaries
        into structured Position objects.
        """
        parsed_positions = [Position.from_raw(position) for position in data]
        return cls(positions=parsed_positions)
    
class ClosedPosition(BaseModel):
    symbol: str
    status: int
    order: Order

    @classmethod
    def from_raw(cls, data: dict) -> "ClosedPosition":
        return cls(
            symbol=data["symbol"],
            status=data["status"],
            order=Order.from_raw(data["body"])
        )
        
class ClosedPositionList(BaseModel):
    """
    Represents a list of ClosedPosition objects returned from the Alpaca API.
    """

    closedPositions: List[ClosedPosition]

    @classmethod
    def from_raw(cls, data: List[dict]) -> "ClosedPositionList":
        """
        Factory method to parse a raw list of order dictionaries
        into structured ClosedPosition objects.
        """
        parsed_closed_position = [ClosedPosition.from_raw(closedPosition) for closedPosition in data]
        return cls(closedPositions=parsed_closed_position)