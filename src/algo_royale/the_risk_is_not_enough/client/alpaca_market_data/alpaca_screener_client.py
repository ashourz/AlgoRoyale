## client\alpaca_market_data\alpaca_screener_client.py

from typing import Optional
from algo_royale.the_risk_is_not_enough.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.shared.models.alpaca_market_data.alpaca_active_stock import MostActiveStocksResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_market_mover import MarketMoversResponse
from algo_royale.shared.models.alpaca_market_data.enums import ActiveStockFilter
from algo_royale.the_risk_is_not_enough.config.config import ALPACA_PARAMS
   

class AlpacaScreenerClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock screener data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaScreenerClient"
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_PARAMS["base_url_data_v1beta1"] 
    
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
            endpoint="screener/stocks/most-actives",
            params=params
        )
        
        return MostActiveStocksResponse.from_raw(response)
                
    async def fetch_market_movers(
        self,
        top: int = 10
    ) -> Optional[MarketMoversResponse]:
        """Fetch market movers data from Alpaca."""

        if not isinstance(top, int) or top <= 0:
            raise ValueError("top must be a positive integer")
        
        params = {
            "top": min(top, 50),  # Alpaca limits to 50
        }
                
        response = await self.get(
            endpoint="screener/stocks/movers",
            params=params
        )
        
        return MarketMoversResponse.from_raw(response)