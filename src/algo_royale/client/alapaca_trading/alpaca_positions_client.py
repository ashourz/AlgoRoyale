# src/algo_royale/client/alpaca_corporate_action_client.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.client.exceptions import MissingParameterError, ParameterConflictError
from httpx import HTTPStatusError
from models.alpaca_trading.alpaca_order import DeleteOrdersResponse, OrderListResponse, Order, StopLoss, TakeProfit
from models.alpaca_trading.alpaca_position import ClosedPosition, ClosedPositionList, PositionList
from models.alpaca_trading.enums import OrderClass, OrderSide, OrderStatus, OrderStatusFilter, OrderType, PositionIntent, SortDirection, TimeInForce
from config.config import ALPACA_TRADING_URL

class AlpacaPositionsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for positions data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaPositionsClient"    
    
    def get_all_open_positions(
        self
    ) -> Optional[PositionList]:
        """
        Get all open positions.

        Returns:
            - PositionList object or None if no response.
        """

        response_json = self._get(
            url=f"{self.base_url}/positions"
        ).json()

        if response_json is None:
            self._logger.warning("No position response received.")
            return None

        return PositionList.from_raw(response_json)
    
    def get_open_position_by_symbol_or_asset_id(
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
            response_json = self._get(
                url=f"{self.base_url}/positions/{symbol_or_asset_id}",
            ).json()


            if response_json is None:
                self._logger.warning("No position response received.")
                return None

            return PositionList.from_raw(response_json)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                # Handle the 404 error with a custom message
                if 'symbol not found' in e.response.text:
                    return {"error": "Symbol not found", "message": f"Symbol {symbol_or_asset_id} not found in your positions."}
                else:
                    # If the error is not the expected "symbol not found", raise the error again
                    raise e
            else:
                # Raise any other HTTP status errors
                raise e
    
    def close_position_by_symbol_or_asset_id(
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


        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response = self._delete(
            url=f"{self.base_url}/positions/{symbol_or_asset_id}",
            params=params
        )
        
        if response.status_code == 207 and response.text == "[]":
            return None

        response_json = response.json()

        if response_json is None:
            self._logger.warning("No closed positions response received.")
            return None

        return ClosedPositionList.from_raw(response_json) 

            
    def close_all_positions(
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
            
        response = self._delete(
            url=f"{self.base_url}/positions",
            params =params
        )

        if response.status_code == 207 and response.text == "[]":
            return None

        response_json = response.json()

        if response_json is None:
            self._logger.warning("No closed positions response received.")
            return None

        return ClosedPositionList.from_raw(response_json) 