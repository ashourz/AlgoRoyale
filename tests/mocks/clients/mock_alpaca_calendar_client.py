from datetime import datetime

from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import (
    AlpacaCalendarClient,
)
from algo_royale.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaCalendarClient(AlpacaCalendarClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        self.return_empty = False
        self.throw_exception = False

    async def fetch_calendar(self, start=None, end=None, date_type=None):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaCalendarClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return CalendarList(calendars=[])
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
