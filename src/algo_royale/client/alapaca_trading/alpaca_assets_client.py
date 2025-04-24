# src/algo_royale/client/alpaca_news_client.py

from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_asset import Asset
from config.config import ALPACA_TRADING_URL

class AlpacaAssetsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaAssetsClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL
    
    def fetch_assets(
            self,
            status: Optional[str] = None,
            asset_class: str = "us_equity",
            exchange: Optional[str] = None
        ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        params = {}
        for k, v in {
            "status": status,
            "asset_class": asset_class,
            "exchange": exchange
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                

        response = self.get(
            endpoint=f"{self.base_url}/assets",
            params=params
        )
   
        return Asset.parse_assets(response)
    
    def fetch_asset_by_symbol_or_id(
            self,
            symbol_or_asset_id: str
        ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        response = self.get(
            endpoint=f"{self.base_url}/assets/{symbol_or_asset_id}"
        )
        
        return Asset.from_raw(response)


            