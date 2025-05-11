# src/algo_royale/service/alpaca_screener_service.py

from typing import Optional
from algo_royale.models.alpaca_market_data.enums import ActiveStockFilter
from algo_royale.models.alpaca_market_data.alpaca_active_stock import MostActiveStocksResponse
from algo_royale.models.alpaca_market_data.alpaca_market_mover import MarketMoversResponse

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import AlpacaScreenerClient


class AlpacaScreenerService:
    """
    Service class that wraps AlpacaScreenerClient to provide streamlined access
    to stock screener data, such as most active stocks and market movers.
    """

    def __init__(self, client: Optional[AlpacaScreenerClient] = None):
        self.client = client or AlpacaScreenerClient()

    async def get_most_active_stocks(
        self,
        by: ActiveStockFilter,
        top: int = 10
    ) -> Optional[MostActiveStocksResponse]:
        """
        Fetch most active stocks using a specific filter (e.g., VOLUME or TRADES).
        """
        return await self.client.fetch_active_stocks(by=by, top=top)

    async def get_market_movers(
        self,
        top: int = 10
    ) -> Optional[MarketMoversResponse]:
        """
        Fetch market movers (top gainers and losers).
        """
        return await self.client.fetch_market_movers(top=top)
