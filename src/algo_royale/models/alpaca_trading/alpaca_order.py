# src/models/alpaca_models/alpaca_trading/alpaca_order.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from algo_royale.models.alpaca_trading.enums.enums import (
    OrderClass,
    OrderSide,
    OrderStatus,
    OrderType,
    TimeInForce,
)


class TakeProfit(BaseModel):
    """
    Parameters for the take-profit leg of advanced orders.

    Attributes:
    - limit_price (float): The price at which to take profit.
    """

    limit_price: float = Field(
        ...,
        description="The price at which to take profit (required for bracket orders)",
    )


class StopLoss(BaseModel):
    """
    Parameters for the stop-loss leg of advanced orders.

    Attributes:
    - stop_price (float): The stop trigger price (required).
    - limit_price (Optional[float]): If provided, turns this into a stop-limit order.
    """

    stop_price: float = Field(
        ..., description="Trigger price to activate the stop-loss (required)"
    )
    limit_price: Optional[float] = Field(
        None, description="Limit price for stop-limit order (optional)"
    )


class Order(BaseModel):
    """
    Represents an order response from the Alpaca API.

    Attributes:
        id (str): Unique identifier for the order.
        client_order_id (str): Unique identifier for the client order.
        created_at (datetime): The timestamp when the order was created.
        updated_at (datetime): The timestamp when the order was last updated.
        submitted_at (datetime): The timestamp when the order was submitted.
        filled_at (Optional[datetime]): The timestamp when the order was filled, if applicable.
        expired_at (Optional[datetime]): The timestamp when the order expired, if applicable.
        canceled_at (Optional[datetime]): The timestamp when the order was canceled, if applicable.
        failed_at (Optional[datetime]): The timestamp when the order failed, if applicable.
        replaced_at (Optional[datetime]): The timestamp when the order was replaced, if applicable.
        replaced_by (Optional[str]): The order ID that replaced this order, if applicable.
        replaces (Optional[str]): The order ID this order is replacing, if applicable.
        asset_id (str): The asset identifier associated with the order.
        symbol (str): The symbol for the asset, like "AAPL".
        asset_class (str): The asset class type, like "us_equity".
        notional (Optional[float]): The notional amount of the order, if applicable.
        qty (float): The quantity of the asset to buy or sell.
        filled_qty (float): The quantity that has been filled so far.
        filled_avg_price (Optional[float]): The average price at which the order was filled, if applicable.
        order_class (Optional[OrderClass]): The class of the order, like "simple", "bracket", etc.
        order_type (OrderType): The type of the order (e.g., "limit", "market").
        type (OrderType): The order type (e.g., "limit", "market").
        side (OrderSide): The side of the order ("buy" or "sell").
        time_in_force (str): The time in force for the order (e.g., "gtc", "day").
        limit_price (float): The price at which the asset should be bought or sold, for limit orders.
        stop_price (Optional[float]): The stop price for stop-limit orders, if applicable.
        status (OrderStatus): The current status of the order (e.g., "accepted", "filled").
        extended_hours (bool): Whether the order is eligible for extended hours trading.
        legs (Optional[list[str]]): List of associated orders if the order is a multi-leg order.
        trail_percent (Optional[float]): The trailing percentage for trailing stop orders, if applicable.
        trail_price (Optional[float]): The trailing price for trailing stop orders, if applicable.
        hwm (Optional[str]): The high water mark, if applicable.
        subtag (Optional[str]): Additional tag, if applicable.
        source (Optional[str]): The source of the order, if applicable.
    """

    id: str
    client_order_id: str

    created_at: datetime
    updated_at: datetime
    submitted_at: datetime

    filled_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    replaced_at: Optional[datetime] = None

    replaced_by: Optional[str] = None
    replaces: Optional[str] = None

    asset_id: str
    symbol: str
    asset_class: str

    notional: Optional[float] = None
    qty: float
    filled_qty: float
    filled_avg_price: Optional[float] = None

    order_class: Optional[OrderClass] = None
    order_type: OrderType
    type: OrderType  # Duplicate field sometimes used in APIs

    side: OrderSide
    time_in_force: TimeInForce

    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trail_percent: Optional[float] = None
    trail_price: Optional[float] = None

    hwm: Optional[float] = None  # high water mark for trailing stops

    status: OrderStatus

    extended_hours: bool
    legs: Optional[list[str]] = None
    subtag: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = False  # Keep enums in their enum form, not strings

    @classmethod
    def from_raw(cls, data: dict) -> "Order":
        """
        Factory method to convert raw API data into a structured OrderResponse object.
        Converts date strings to datetime, and string values to enums or floats.
        """
        # Convert ISO datetime strings to datetime objects
        datetime_fields = [
            "created_at",
            "updated_at",
            "submitted_at",
            "filled_at",
            "expired_at",
            "canceled_at",
            "failed_at",
            "replaced_at",
        ]
        for field in datetime_fields:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))

        # Convert enum fields
        enum_mappings = {
            "order_class": OrderClass,
            "order_type": OrderType,
            "order_status": OrderStatus,
            "type": OrderType,
            "side": OrderSide,
            "time_in_force": TimeInForce,
        }
        for key, enum_cls in enum_mappings.items():
            if key in data:
                if data[key] == "":
                    data[key] = None
                elif isinstance(data[key], str):
                    try:
                        data[key] = enum_cls(data[key])
                    except ValueError:
                        pass  # Leave as-is if unknown enum

        # Convert float fields
        float_fields = [
            "qty",
            "filled_qty",
            "notional",
            "filled_avg_price",
            "limit_price",
            "stop_price",
            "trail_percent",
            "trail_price",
            "hwm",
        ]
        for field in float_fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (TypeError, ValueError):
                    pass  # Ignore conversion error and keep original

        # Ensure qty and filled_qty are never None (default to 0.0)
        if data.get("qty") is None:
            data["qty"] = 0.0
        if data.get("filled_qty") is None:
            data["filled_qty"] = 0.0

        return cls(**data)


class OrderListResponse(BaseModel):
    """
    Represents a list of OrderResponse objects returned from the Alpaca API.
    """

    orders: list[Order]

    @classmethod
    def from_raw(cls, data: list[dict]) -> "OrderListResponse":
        """
        Factory method to parse a raw list of order dictionaries
        into structured OrderResponse objects.
        """
        parsed_orders = [Order.from_raw(order) for order in data]
        return cls(orders=parsed_orders)


class DeleteOrderStatus(BaseModel):
    """Represents the status of a single deleted order."""

    id: str
    status: int


class DeleteOrdersResponse(BaseModel):
    """Represents the multi-status response when deleting multiple orders."""

    orders: list[DeleteOrderStatus]

    @classmethod
    def from_raw(cls, data: list[dict]) -> "DeleteOrdersResponse":
        """
        Converts a raw list of dictionaries to a DeleteOrdersResponse.

        Args:
            data (list[dict]): The raw JSON response from the API.

        Returns:
            DeleteOrdersResponse: The parsed model.
        """
        return cls(orders=[DeleteOrderStatus(**item) for item in data])
