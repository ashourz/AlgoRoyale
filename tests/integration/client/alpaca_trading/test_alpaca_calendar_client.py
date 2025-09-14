# src/tests/integration/client/test_alpaca_calendar_client.py


from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import (
    AlpacaCalendarClient,
)
from algo_royale.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaCalendarClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    fake_calendar = Calendar(
        trading_day="2024-01-01",
        open="2024-01-01T09:30:00",
        close="2024-01-01T16:00:00",
        session_open="2024-01-01T09:00:00",
        session_close="2024-01-01T17:00:00",
        settlement_date="2024-01-02",
    )
    monkeypatch.setattr(
        client,
        "fetch_calendar",
        AsyncMock(return_value=CalendarList(calendars=[fake_calendar])),
    )
    yield client
    await client.aclose()


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

            alpaca_client.logger.debug(
                f"Calendar: {calendar.trading_day} - Open: {calendar.open} Close: {calendar.close}"
            )

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
            assert start.date() <= cal.trading_day <= end.date(), (
                f"{cal.trading_day} is outside the expected date range"
            )
