# src/tests/integration/client/test_alpaca_calendar_client.py

from datetime import datetime
from shared.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList
from the_risk_is_not_enough.client.alpaca_trading.alpaca_calendar_client import AlpacaCalendarClient
import pytest

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType



# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()


@pytest.fixture(scope="class")
def alpaca_calendar_client():
    return AlpacaCalendarClient()


@pytest.mark.asyncio
class TestAlpacaCalendarClientIntegration:

    def test_fetch_calendar_default(self, alpaca_calendar_client):
        """
        Test fetching default calendar data from Alpaca with no parameters.
        """
        result = alpaca_calendar_client.fetch_calendar()

        assert result is not None
        assert isinstance(result, CalendarList)
        assert isinstance(result.calendars, list)
        assert len(result.calendars) > 0, "Calendar list should not be empty"

        for calendar in result.calendars:
            assert isinstance(calendar, Calendar)
            assert calendar.trading_day is not None
            assert calendar.open is not None
            assert calendar.close is not None
            assert calendar.session_open is not None
            assert calendar.session_close is not None
            assert calendar.settlement_date is not None

            logger.debug(f"Calendar: {calendar.trading_day} - Open: {calendar.open} Close: {calendar.close}")

    def test_fetch_calendar_with_date_range(self, alpaca_calendar_client):
        """
        Test fetching calendar data within a specific date range.
        """
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)

        result = alpaca_calendar_client.fetch_calendar(start=start, end=end)

        assert result is not None
        assert isinstance(result, CalendarList)
        assert all(isinstance(cal, Calendar) for cal in result.calendars)

        for cal in result.calendars:
            assert start.date() <= cal.trading_day <= end.date(), \
                f"{cal.trading_day} is outside the expected date range"
