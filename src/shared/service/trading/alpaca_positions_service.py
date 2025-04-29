# src/algo_royale/services/alpaca_trading/alpaca_positions_service.py

from typing import Optional
from shared.models.alpaca_trading.alpaca_position import ClosedPositionList, PositionList
from the_risk_is_not_enough.client.alpaca_trading.alpaca_positions_client import AlpacaPositionsClient
from the_risk_is_not_enough.client.exceptions import MissingParameterError, ParameterConflictError

class AlpacaPositionsService:
    """Service class to manage positions data and actions on Alpaca API."""

    def __init__(self):
        self.client = AlpacaPositionsClient()

    def get_all_open_positions(self) -> Optional[PositionList]:
        """
        Fetch all open positions from Alpaca.

        Returns:
            PositionList: List of open positions, or None if no data is found.
        """
        return self.client.get_all_open_positions()

    def get_open_position_by_symbol_or_asset_id(self, symbol_or_asset_id: str) -> Optional[PositionList]:
        """
        Fetch an open position by symbol or asset ID.

        Parameters:
            symbol_or_asset_id (str): The symbol or asset ID of the position to fetch.

        Returns:
            PositionList: A single position or None if no position is found.
        """
        if not symbol_or_asset_id:
            raise MissingParameterError("Missing required parameter: 'symbol_or_asset_id'.")
        return self.client.get_open_position_by_symbol_or_asset_id(symbol_or_asset_id)

    def close_position_by_symbol_or_asset_id(
        self, 
        symbol_or_asset_id: str, 
        qty: Optional[float] = None, 
        percentage: Optional[float] = None
    ) -> Optional[ClosedPositionList]:
        """
        Close a position by its symbol or asset ID.

        Parameters:
            symbol_or_asset_id (str): The symbol or asset ID of the position to close.
            qty (float): The number of shares to liquidate (optional).
            percentage (float): The percentage of the position to liquidate (optional).

        Returns:
            ClosedPositionList: The list of closed positions, or None if no data is found.
        """
        if not symbol_or_asset_id:
            raise MissingParameterError("Missing required parameter: 'symbol_or_asset_id'.")
        if qty and percentage:
            raise ParameterConflictError("Specify either 'qty' or 'percentage' or neither, not both.")
        
        return self.client.close_position_by_symbol_or_asset_id(symbol_or_asset_id, qty, percentage)

    def close_all_positions(self, cancel_orders: Optional[bool] = None) -> Optional[ClosedPositionList]:
        """
        Close all open positions.

        Parameters:
            cancel_orders (bool): Flag to indicate whether to cancel orders when closing positions (optional).

        Returns:
            ClosedPositionList: The list of closed positions, or None if no data is found.
        """
        return self.client.close_all_positions(cancel_orders)
