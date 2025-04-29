## client\alpaca_trading\alpaca_assets_client.py

from typing import List, Optional
from the_risk_is_not_enough.client.alpaca_base_client import AlpacaBaseClient
from the_risk_is_not_enough.client.exceptions import AlpacaAssetNotFoundException, AlpacaResourceNotFoundException
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

        params = {
            "status": status,
            "asset_class": asset_class,
            "exchange": exchange
        }
                
        try:
            response = self.get(
                endpoint="assets",
                params=params
            )
            return Asset.parse_assets(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(f"Asset not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaAssetNotFoundException(e.message)
    
    
    def fetch_asset_by_symbol_or_id(
            self,
            symbol_or_asset_id: str
        ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        try:
            response = self.get(
                endpoint=f"assets/{symbol_or_asset_id}"
            )
            return Asset.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(f"Asset not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaAssetNotFoundException(e.message)

            