## client\alpaca_trading\alpaca_positions_client.py

from typing import Optional
from algo_royale.the_risk_is_not_enough.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.the_risk_is_not_enough.client.exceptions import AlpacaPositionNotFoundException, AlpacaResourceNotFoundException, MissingParameterError, ParameterConflictError
from algo_royale.the_risk_is_not_enough.config.config import ALPACA_TRADING_URL
from algo_royale.shared.models.alpaca_trading.alpaca_position import ClosedPositionList, PositionList

class AlpacaPositionsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for positions data.""" 


    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaPositionsClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL
    
    async def get_all_open_positions(
        self
    ) -> Optional[PositionList]:
        """
        Get all open positions.

        Returns:
            - PositionList object or None if no response.
        """

        response = await self.get(
            endpoint="positions"
        )

        return PositionList.from_raw(response)
    
    async def get_open_position_by_symbol_or_asset_id(
        self,
        symbol_or_asset_id: str
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
            raise MissingParameterError("Missing required parameter: 'symbol_or_asset_id'.")
        if qty and percentage:
            raise ParameterConflictError("Specify either 'qty' or 'percentage' or neither, not both.")
        
        params = {}
        # --- Build request payload ---
        if qty:
            params["qty"] = qty
        if percentage:
            params["percentage"] = percentage
        try:
            response = await self.delete(
                endpoint=f"positions/{symbol_or_asset_id}",
                params=params
            )
            return ClosedPositionList.from_raw(response) 
        except AlpacaResourceNotFoundException as e:
            raise AlpacaPositionNotFoundException(e.message)
            
    async def close_all_positions(
        self,
        cancel_orders: Optional[bool] = None
    ) -> Optional[ClosedPositionList]:
        """
        Close all positions.

        Returns:
            - ClosedPositionList object or None if no response.
        """
        params = {}
        if cancel_orders:
            params["cancel_orders"] = cancel_orders
            
        response = await self.delete(
            endpoint="positions",
            params =params
        )

        return ClosedPositionList.from_raw(response) 