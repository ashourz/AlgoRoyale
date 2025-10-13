# src/models/alpaca_models/alpaca_trading/alpaca_order.py

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel


class Clock(BaseModel):
    """
    Represents the current market clock status.

    Attributes:
        timestamp (datetime): The current server time.
        is_open (bool): Whether the market is currently open.
        next_open (datetime): The next scheduled market open time.
        next_close (datetime): The next scheduled market close time.
    """

    timestamp: datetime
    is_open: bool
    next_open: datetime
    next_close: datetime

    @classmethod
    def from_raw(cls, data: Dict[str, Any]) -> "Clock":
        """
        Parses raw dictionary data from the API into a Clock object.

        Args:
            data (Dict[str, Any]): Raw clock data from the API.

        Returns:
            Clock: Parsed Clock object.
        """
        parsed_data = {
            "timestamp": datetime.fromisoformat(data["timestamp"]),
            "is_open": data["is_open"],
            "next_open": datetime.fromisoformat(data["next_open"]),
            "next_close": datetime.fromisoformat(data["next_close"]),
        }

        return cls(**parsed_data)