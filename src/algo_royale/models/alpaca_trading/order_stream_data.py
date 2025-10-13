from datetime import datetime

from pydantic import BaseModel

from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent


class OrderStreamData(BaseModel):
    """Represents a single order update event in the Alpaca trading system.
    Attributes:
        event (str): Type of event (e.g., "fill", "update").
        price (float): Price at which the order was filled or updated.
        timestamp (datetime): Timestamp of the event.
        position_qty (int): Quantity of the position affected by the order.
        order (Order): The order object associated with this event.
    """

    event: OrderStreamEvent
    price: float
    timestamp: datetime
    position_qty: int
    order: Order

    @classmethod
    def from_dict(cls, data: dict) -> "OrderStreamData":
        """Create an OrderStreamData instance from a dictionary."""
        return cls(
            event=OrderStreamEvent.from_name(data.get("event")),
            price=data.get("price"),
            timestamp=datetime.fromisoformat(data.get("timestamp")),
            position_qty=data.get("position_qty"),
            order=Order.from_raw(data.get("order")),
        )
