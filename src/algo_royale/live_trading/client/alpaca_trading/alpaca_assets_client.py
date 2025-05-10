## client\alpaca_trading\alpaca_assets_client.py

from typing import Optional
from algo_royale.live_trading.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.live_trading.client.exceptions import AlpacaAssetNotFoundException, AlpacaResourceNotFoundException
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from algo_royale.live_trading.config.live_trading_config import ALPACA_TRADING_URL

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
    
    async def fetch_assets(
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
            response = await self.get(
                endpoint="assets",
                params=params
            )
            return Asset.parse_assets(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(f"Asset not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaAssetNotFoundException(e.message)
    
    
    async def fetch_asset_by_symbol_or_id(
            self,
            symbol_or_asset_id: str
        ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        try:
            response = await self.get(
                endpoint=f"assets/{symbol_or_asset_id}"
            )
            return Asset.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(f"Asset not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaAssetNotFoundException(e.message)

            