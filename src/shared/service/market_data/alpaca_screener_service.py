# src/algo_royale/service/alpaca_screener_service.py

from typing import Optional
from models.alpaca_market_data.enums import ActiveStockFilter
from models.alpaca_market_data.alpaca_active_stock import MostActiveStocksResponse
from models.alpaca_market_data.alpaca_market_mover import MarketMoversResponse

from the_risk_is_not_enough.client.alpaca_market_data.alpaca_screener_client import AlpacaScreenerClient


class AlpacaScreenerService:
    """
    Service class that wraps AlpacaScreenerClient to provide streamlined access
    to stock screener data, such as most active stocks and market movers.
    """

    def __init__(self, client: Optional[AlpacaScreenerClient] = None):
        self.client = client or AlpacaScreenerClient()

    def get_most_active_stocks(
        self,
        by: ActiveStockFilter,
        top: int = 10
    ) -> Optional[MostActiveStocksResponse]:
        """
        Fetch most active stocks using a specific filter (e.g., VOLUME or TRADES).
        """
        return self.client.fetch_active_stocks(by=by, top=top)

    def get_market_movers(
        self,
        top: int = 10
    ) -> Optional[MarketMoversResponse]:
        """
        Fetch market movers (top gainers and losers).
        """
        return self.client.fetch_market_movers(top=top)
