# src/algo_royale/client/alpaca_screener_client.py

from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_models.alpaca_active_stock import MostActiveStocksResponse
from models.alpaca_models.alpaca_market_mover import MarketMoversResponse
from config.config import ALPACA_PARAMS

class ActiveStockFilter(Enum):
    """
    Enum for different types of active stock filters.
    
    Types:
    - VOLUME: Filter based on trading volume.
    - TRADES: Filter based on number of trades.
    """
    VOLUME = "volume"
    TRADES = "trades"
    

class AlpacaScreenerClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock screener data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_PARAMS["base_url_data_v1beta1"] 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaScreenerClient"
    
    def fetch_active_stocks(
        self,
        by: ActiveStockFilter,
        top: int = 10,
    ) -> Optional[MostActiveStocksResponse]:
        """Fetch active stocks data from Alpaca."""

        if not isinstance(by, ActiveStockFilter):
            raise ValueError("by must be an instance of ActiveStockFilter")
        if not isinstance(top, int) or top <= 0:
            raise ValueError("top must be a positive integer")
        
        params = {}
        for k, v in {
            "by": by.value,
            "top": min(top, 100),  # Alpaca limits to 100
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/screener/stocks/most-actives",
            params=params
        )
        
        if responseJson is None:
            self._logger.warning("No active stocks data found")
            return None
        
        return MostActiveStocksResponse.from_raw(responseJson)
                
    def fetch_market_movers(
        self,
        top: int = 10
    ) -> Optional[MarketMoversResponse]:
        """Fetch market movers data from Alpaca."""

        if not isinstance(top, int) or top <= 0:
            raise ValueError("top must be a positive integer")
        
        params = {}
        for k, v in {
            "top": min(top, 50),  # Alpaca limits to 50
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/screener/stocks/movers",
            params=params
        )
        
        if responseJson is None:
            self._logger.warning("No market movers data found")
            return None
        
        return MarketMoversResponse.from_raw(responseJson)