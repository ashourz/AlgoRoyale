## client\alpaca_trading\alpaca_assets_client.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.exceptions import (
    AlpacaAssetNotFoundException,
    AlpacaResourceNotFoundException,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_asset import Asset


class AlpacaAssetsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data."""

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
        return "AlpacaAssetsClient"

    async def fetch_assets(
        self,
        status: Optional[str] = None,
        asset_class: str = "us_equity",
        exchange: Optional[str] = None,
    ) -> Optional[list[Asset]]:
        """Fetch asset data from Alpaca."""

        params = {"status": status, "asset_class": asset_class, "exchange": exchange}

        try:
            response = await self.get(endpoint="assets", params=params)
            return Asset.parse_assets(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(
                f"Asset not found. Code:{e.status_code} | Message:{e.message}"
            )
            raise AlpacaAssetNotFoundException(e.message)

    async def fetch_asset_by_symbol_or_id(
        self, symbol_or_asset_id: str
    ) -> Optional[Asset]:
        """Fetch asset data from Alpaca."""

        try:
            response = await self.get(endpoint=f"assets/{symbol_or_asset_id}")
            return Asset.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(
                f"Asset not found. Code:{e.status_code} | Message:{e.message}"
            )
            raise AlpacaAssetNotFoundException(e.message)
