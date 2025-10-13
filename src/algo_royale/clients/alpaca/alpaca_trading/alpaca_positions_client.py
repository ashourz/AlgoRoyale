## client\alpaca_trading\alpaca_positions_client.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.exceptions import (
    AlpacaPositionNotFoundException,
    AlpacaResourceNotFoundException,
    MissingParameterError,
    ParameterConflictError,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_position import (
    ClosedPositionList,
    PositionList,
)


class AlpacaPositionsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for positions data."""

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
        return "AlpacaPositionsClient"

    async def fetch_all_open_positions(self) -> Optional[PositionList]:
        """
        Get all open positions.

        Returns:
            - PositionList object or None if no response.
        """

        response = await self.get(endpoint="positions")

        return PositionList.from_raw(response)

    async def fetch_open_position_by_symbol_or_asset_id(
        self, symbol_or_asset_id: str
    ) -> Optional[PositionList]:
        """
        Get open position by symbol or asset id

        Parameters:
            - symbol_or_asset_id (str) : symbol or assetId

        Returns:
            - PositionList object or None if no response.
        """
        try:
            response = await self.get(
                endpoint=f"positions/{symbol_or_asset_id}",
            )

            # If response is a dict (single position), wrap in a list
            if isinstance(response, dict):
                response = [response]
            return PositionList.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            raise AlpacaPositionNotFoundException(e.message)

    async def close_position_by_symbol_or_asset_id(
        self,
        symbol_or_asset_id: str,
        qty: Optional[float] = None,
        percentage: Optional[float] = None,
    ) -> Optional[ClosedPositionList]:
        """
        Close an position by its symbol or assetId

        Parameters:
            - symbol_or_asset_id (str) : symbol or assetId
            - qty (float) : the number of shares to liquidate.
                Can accept up to 9 decimal points. Cannot work with percentage
            - percentage (float) : percentage of position to liquidate.
                Must be between 0 and 100. Would only sell fractional if position is originally fractional.
                Can accept up to 9 decimal points. Cannot work with qty

        Returns:
            - ClosedPositionList object or None if no response.
        """
        if not symbol_or_asset_id:
            raise MissingParameterError(
                "Missing required parameter: 'symbol_or_asset_id'."
            )
        if qty and percentage:
            raise ParameterConflictError(
                "Specify either 'qty' or 'percentage' or neither, not both."
            )

        params = {}
        # --- Build request payload ---
        if qty:
            params["qty"] = qty
        if percentage:
            params["percentage"] = percentage
        try:
            response = await self.delete(
                endpoint=f"positions/{symbol_or_asset_id}", params=params
            )
            return ClosedPositionList.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            raise AlpacaPositionNotFoundException(e.message)

    async def close_all_positions(
        self, cancel_orders: Optional[bool] = None
    ) -> Optional[ClosedPositionList]:
        """
        Close all positions.

        Returns:
            - ClosedPositionList object or None if no response.
        """
        params = {}
        if cancel_orders:
            params["cancel_orders"] = cancel_orders

        response = await self.delete(endpoint="positions", params=params)

        return ClosedPositionList.from_raw(response)
