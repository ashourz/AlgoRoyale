## client\alpaca_trading\alpaca_calendar_client.py


from datetime import datetime
from typing import Optional

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_calendar import CalendarList
from algo_royale.models.alpaca_trading.enums.enums import CalendarDateType


class AlpacaCalendarClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data."""

    def __init__(
        self,
        logger: Loggable,
        base_url: str,
        api_key: str,
        api_secret: str,
        api_key_header: str,
        api_secret_header: str,
        http_timeout: int = 10,
        reconnect_delay: int = 5,
        keep_alive_timeout: int = 20,
    ):
        """Initialize the AlpacaStockClient with trading configuration."""
        super().__init__(
            logger=logger,
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret,
            api_key_header=api_key_header,
            api_secret_header=api_secret_header,
            http_timeout=http_timeout,
            reconnect_delay=reconnect_delay,
            keep_alive_timeout=keep_alive_timeout,
        )

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCalendarClient"

    async def fetch_calendar(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        date_type: Optional[CalendarDateType] = None,
    ) -> Optional[CalendarList]:
        """Fetch calendar data from Alpaca."""

        params = {}

        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if date_type:
            params["date_type"] = date_type

        response = await self.get(endpoint="calendar", params=params)

        return CalendarList.from_raw(response)
