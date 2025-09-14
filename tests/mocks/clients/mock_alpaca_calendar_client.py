from datetime import datetime

from algo_royale.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaCalendarClient:
    def __init__(self):
        self.logger = MockLoggable()

    async def fetch_calendar(self, start=None, end=None):
        fake_calendar = Calendar(
            trading_day=datetime(2024, 1, 1).date(),
            open="2024-01-01T09:30:00",
            close="2024-01-01T16:00:00",
            session_open="2024-01-01T09:00:00",
            session_close="2024-01-01T17:00:00",
            settlement_date="2024-01-02",
        )
        return CalendarList(calendars=[fake_calendar])

    async def aclose(self):
        pass
