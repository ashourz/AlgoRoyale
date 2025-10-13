# src/algo_royale/service/alpaca_screener_service.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    AlpacaScreenerClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_active_stock import (
    MostActiveStocksResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_market_mover import (
    MarketMoversResponse,
)
from algo_royale.models.alpaca_market_data.enums import ActiveStockFilter


class ScreenerAdapter:
    """
    Service class that wraps AlpacaScreenerClient to provide streamlined access
    to stock screener data, such as most active stocks and market movers.
    """

    def __init__(self, client: AlpacaScreenerClient, logger: Loggable):
        """
        Initialize the ScreenerAdapter with the AlpacaScreenerClient and a logger.

        Args:
            client (AlpacaScreenerClient): Instance of AlpacaScreenerClient for API calls.
            logger (Loggable): Logger instance for logging events and errors.
        """
        self.client = client
        self.logger = logger

    async def get_most_active_stocks(
        self, by: ActiveStockFilter, top: int = 10
    ) -> Optional[MostActiveStocksResponse]:
        """
        Fetch most active stocks using a specific filter (e.g., VOLUME or TRADES).
        """
        return await self.client.fetch_active_stocks(by=by, top=top)

    async def get_market_movers(self, top: int = 10) -> Optional[MarketMoversResponse]:
        """
        Fetch market movers (top gainers and losers).
        """
        return await self.client.fetch_market_movers(top=top)
