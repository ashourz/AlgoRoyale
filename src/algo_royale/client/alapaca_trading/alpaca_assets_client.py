# src/algo_royale/client/alpaca_news_client.py

from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_asset import Asset
from config.config import ALPACA_TRADING_URL

class AlpacaAssetsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaAssetsClient"    
    
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
                

        responseJson = self._get(
            url=f"{self.base_url}/assets",
            params=params
        )

        self._logger.debug(f"Assets: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No asset data available")
            return None       
        
        return Asset.parse_assets(responseJson)
    
    def fetch_asset_by_symbol_or_id(
            self,
            symbol_or_asset_id: str
        ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        responseJson = self._get(
            url=f"{self.base_url}/assets/{symbol_or_asset_id}"
        )

        self._logger.debug(f"Assets: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No asset data available")
            return None       
        
        return Asset.from_raw(responseJson)


            