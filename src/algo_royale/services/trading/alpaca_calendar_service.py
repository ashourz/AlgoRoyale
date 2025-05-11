from typing import Optional
from datetime import datetime
from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import AlpacaCalendarClient
from algo_royale.models.alpaca_trading.alpaca_calendar import CalendarList
from algo_royale.clients.alpaca.exceptions import CalendarNotFoundError

class AlpacaCalendarService:
    """Service class to interact with Alpaca's corporate action calendar data, leveraging AlpacaCalendarClient."""

    def __init__(self, calendar_client: AlpacaCalendarClient):
        """
        Initializes AlpacaCalendarService with the given AlpacaCalendarClient.

        Args:
            calendar_client (AlpacaCalendarClient): The Alpaca client used to interact with the Alpaca API for calendar data.
        """
        self.calendar_client = calendar_client

    async def get_calendar(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        date_type: Optional[str] = None
    ) -> Optional[CalendarList]:
        """
        Fetches corporate action calendar data from the Alpaca API.

        Args:
            start (Optional[datetime]): The start date for the calendar query.
            end (Optional[datetime]): The end date for the calendar query.
            date_type (Optional[str]): The date type to filter by (e.g., "trading_day", "settlement_day").
        
        Returns:
            Optional[CalendarList]: A list of corporate action calendar data retrieved from Alpaca, or None if no calendar data matches.
        """
        calendar = await self.calendar_client.fetch_calendar(start=start, end=end, date_type=date_type)

        if not calendar:
            return None

        return calendar

    async def get_calendar_by_date(self, start: datetime, end: datetime) -> Optional[CalendarList]:
        """
        Fetches corporate action calendar data from the Alpaca API for a specific date range.

        Args:
            start (datetime): The start date for the calendar query.
            end (datetime): The end date for the calendar query.
        
        Returns:
            Optional[CalendarList]: A list of corporate action calendar data retrieved from Alpaca, or None if no calendar data matches.
        
        Raises:
            CalendarNotFoundError: If no calendar data is found for the given date range.
        """
        calendar = await self.calendar_client.fetch_calendar(start=start, end=end)

        if not calendar:
            raise CalendarNotFoundError(f"No corporate action calendar data found for the dates {start} to {end}.")
        
        return calendar
