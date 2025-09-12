from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import (
    AlpacaClockClient,
)
from algo_royale.clients.alpaca.exceptions import ClockNotFoundError
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_clock import Clock


class ClockAdapter:
    """Service class to interact with Alpaca's clock data, leveraging AlpacaClockClient."""

    def __init__(self, clock_client: AlpacaClockClient, logger: Loggable):
        """
        Initializes AlpacaClockService with the given AlpacaClockClient.

        Args:
            clock_client (AlpacaClockClient): The Alpaca client used to interact with the Alpaca API for clock data.
        """
        self.clock_client = clock_client
        self.logger = logger

    async def get_clock(self) -> Optional[Clock]:
        """
        Fetches clock data from the Alpaca API.

        Returns:
            Optional[Clock]: The clock data retrieved from Alpaca, or None if no clock data is found.
        """
        clock = await self.clock_client.fetch_clock()

        if not clock:
            return None

        return clock

    async def get_clock_or_raise(self) -> Clock:
        """
        Fetches clock data from the Alpaca API and raises an exception if no data is found.

        Returns:
            Clock: The clock data retrieved from Alpaca.

        Raises:
            ClockNotFoundError: If no clock data is found.
        """
        clock = await self.clock_client.fetch_clock()

        if not clock:
            raise ClockNotFoundError("Clock data could not be retrieved from Alpaca.")

        return clock
