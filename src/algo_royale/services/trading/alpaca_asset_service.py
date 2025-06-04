from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import (
    AlpacaAssetsClient,
)
from algo_royale.clients.alpaca.exceptions import AssetNotFoundError
from algo_royale.models.alpaca_trading.alpaca_asset import Asset


class AlpacaAssetService:
    """Service class to interact with Alpaca's assets data, leveraging AlpacaAssetsClient."""

    def __init__(self, assets_client: AlpacaAssetsClient):
        """
        Initializes AlpacaAssetService with the given AlpacaAssetsClient.

        Args:
            assets_client (AlpacaAssetsClient): The Alpaca client used to interact with the Alpaca API for asset data.
        """
        self.assets_client = assets_client

    async def get_assets(
        self,
        status: Optional[str] = None,
        asset_class: str = "us_equity",
        exchange: Optional[str] = None,
    ) -> Optional[list[Asset]]:
        """
        Fetches asset data from the Alpaca API.

        Args:
            status (Optional[str]): Filter assets by status (e.g., active, inactive).
            asset_class (str): The asset class to filter by (default is "us_equity").
            exchange (Optional[str]): The exchange to filter by (e.g., NYSE, NASDAQ).

        Returns:
            Optional[list[Asset]]: A list of assets retrieved from Alpaca, or None if no assets match.
        """
        assets = await self.assets_client.fetch_assets(
            status=status, asset_class=asset_class, exchange=exchange
        )

        if not assets:
            return None

        return assets

    async def get_asset_by_symbol_or_id(
        self, symbol_or_asset_id: str
    ) -> Optional[Asset]:
        """
        Fetches a single asset by symbol or asset ID from the Alpaca API.

        Args:
            symbol_or_asset_id (str): The symbol or asset ID of the asset to retrieve.

        Returns:
            Optional[Asset]: The asset retrieved from Alpaca, or None if no asset is found.

        Raises:
            AssetNotFoundError: If the asset cannot be found in the Alpaca API.
        """
        asset = await self.assets_client.fetch_asset_by_symbol_or_id(symbol_or_asset_id)

        if asset is None:
            raise AssetNotFoundError(
                f"Asset with symbol or ID '{symbol_or_asset_id}' not found."
            )

        return asset
