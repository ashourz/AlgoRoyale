import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import (
    AlpacaCalendarClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_calendar import Calendar, CalendarList


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_calendar_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaCalendarClientIntegration:
    async def test_get_calendar(self, alpaca_client: AlpacaCalendarClient):
        response = await alpaca_client.fetch_calendar()
        assert response is not None
        assert isinstance(response, CalendarList)
        if response.calendars:
            assert isinstance(response.calendars[0], Calendar)
