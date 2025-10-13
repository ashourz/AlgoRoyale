## client\alpaca_market_data\alpaca_screener_client.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_active_stock import (
    MostActiveStocksResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_market_mover import (
    MarketMoversResponse,
)
from algo_royale.models.alpaca_market_data.enums import ActiveStockFilter


class AlpacaScreenerClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock screener data."""

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
        return "AlpacaScreenerClient"

    async def fetch_active_stocks(
        self,
        by: ActiveStockFilter,
        top: int = 10,
    ) -> Optional[MostActiveStocksResponse]:
        """Fetch active stocks data from Alpaca."""

        if not isinstance(by, ActiveStockFilter):
            raise ValueError("by must be an instance of ActiveStockFilter")
        if not isinstance(top, int) or top <= 0:
            raise ValueError("top must be a positive integer")

        params = {
            "by": by.value,
            "top": min(top, 100),  # Alpaca limits to 100
        }

        response = await self.get(
            endpoint="screener/stocks/most-actives", params=params
        )

        return MostActiveStocksResponse.from_raw(response)

    async def fetch_market_movers(
        self, top: int = 10
    ) -> Optional[MarketMoversResponse]:
        """Fetch market movers data from Alpaca."""

        if not isinstance(top, int) or top <= 0:
            raise ValueError("top must be a positive integer")

        params = {
            "top": min(top, 50),  # Alpaca limits to 50
        }

        response = await self.get(endpoint="screener/stocks/movers", params=params)

        return MarketMoversResponse.from_raw(response)
