# src/models/alpaca_models/alpaca_trading/alpaca_order.py

from datetime import datetime, date
from typing import Any, Dict, List
from pydantic import BaseModel


class Calendar(BaseModel):
    """
    The market calendar for equity markets.
    Describes the market open/close, session open/close, and settlement time on a given day.
    """

    trading_day: date
    open: datetime
    close: datetime
    session_open: datetime
    session_close: datetime
    settlement_date: date 

    @classmethod
    def from_raw(cls, data: Dict[str, Any]) -> "Calendar":
        """
        Parses raw dictionary data from the API into a Calendar object.

        Args:
            data (Dict[str, Any]): Raw calendar data with time strings.

        Returns:
            Calendar: Parsed Calendar object with datetime fields.
        """
        date_str = data["date"]

        parsed_data = {
            "trading_day": datetime.strptime(data["date"], "%Y-%m-%d").date(),
            "open": datetime.strptime(f"{date_str} {data['open']}", "%Y-%m-%d %H:%M"),
            "close": datetime.strptime(f"{date_str} {data['close']}", "%Y-%m-%d %H:%M"),
            "session_open": datetime.strptime(f"{date_str} {data['session_open']}", "%Y-%m-%d %H%M"),
            "session_close": datetime.strptime(f"{date_str} {data['session_close']}", "%Y-%m-%d %H%M"),
            "settlement_date": datetime.strptime(data["settlement_date"], "%Y-%m-%d").date(),
        }

        return cls(**parsed_data)


class CalendarList(BaseModel):
    """
    Wrapper for a list of Calendar entries.
    """

    calendars: List[Calendar]

    @classmethod
    def from_raw(cls, data_list: List[Dict[str, Any]]) -> "CalendarList":
        """
        Parses a list of raw dictionary entries into a CalendarList.

        Args:
            data_list (List[Dict[str, Any]]): List of raw calendar entries.

        Returns:
            CalendarList: List wrapped in CalendarList model.
        """
        return cls(calendars=[Calendar.from_raw(item) for item in data_list])
