# src/tests/integration/client/test_alpaca_calendar_client.py

from datetime import datetime
from algo_royale.shared.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList
from algo_royale.the_risk_is_not_enough.client.alpaca_trading.alpaca_calendar_client import AlpacaCalendarClient
import pytest

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType



# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()

@pytest.fixture
async def alpaca_client():
    client = AlpacaCalendarClient()
    yield client
    await client.close()  # Clean up the async client

@pytest.mark.asyncio
class TestAlpacaCalendarClientIntegration:

    async def test_fetch_calendar_default(self, alpaca_client):
        """
        Test fetching default calendar data from Alpaca with no parameters.
        """
        result = await alpaca_client.fetch_calendar()

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

    async def test_fetch_calendar_with_date_range(self, alpaca_client):
        """
        Test fetching calendar data within a specific date range.
        """
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)

        result = await alpaca_client.fetch_calendar(start=start, end=end)

        assert result is not None
        assert isinstance(result, CalendarList)
        assert all(isinstance(cal, Calendar) for cal in result.calendars)

        for cal in result.calendars:
            assert start.date() <= cal.trading_day <= end.date(), \
                f"{cal.trading_day} is outside the expected date range"
