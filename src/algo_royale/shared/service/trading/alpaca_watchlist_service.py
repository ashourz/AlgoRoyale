# src/algo_royale/service/alpaca_watchlist_service.py

from typing import List, Optional
from algo_royale.the_risk_is_not_enough.client.alpaca_trading.alpaca_watchlist_client import AlpacaWatchlistClient
from algo_royale.shared.models.alpaca_trading.alpaca_watchlist import Watchlist, WatchlistListResponse

class AlpacaWatchlistService:
    """Service class for interacting with Alpaca's watchlist data."""
    
    def __init__(self, client: AlpacaWatchlistClient):
        self.client = client

    def get_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for the account.

        Returns:
            - WatchlistListResponse object or None if no response.
        """
        return self.client.get_all_watchlists()

    def get_watchlist_by_id(self, watchlist_id: str) -> Optional[Watchlist]:
        """
        Get a specific watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.get_watchlist_by_id(watchlist_id)

    def get_watchlist_by_name(self, name: str) -> Optional[Watchlist]:
        """
        Get a specific watchlist by name.

        Parameters:
            - name (str) : The watchlist name.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.get_watchlist_by_name(name)

    def create_watchlist(self, name: str, symbols: Optional[List[str]] = None) -> Optional[Watchlist]:
        """
        Create a new watchlist.

        Parameters:
            - name (str) : The name of the watchlist.
            - symbols (List[str]) : Optional list of symbols to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.create_watchlist(name, symbols)

    def update_watchlist_by_id(self, watchlist_id: str, name: str) -> Optional[Watchlist]:
        """
        Update an existing watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - name (str) : The new name of the watchlist.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.update_watchlist_by_id(watchlist_id, name)

    def update_watchlist_by_name(self, name: str, update_name: str) -> Optional[Watchlist]:
        """
        Update an existing watchlist by name.

        Parameters:
            - name (str) : The original name of the watchlist.
            - update_name (str) : The new name of the watchlist.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.update_watchlist_by_name(name, update_name)

    def delete_watchlist_by_id(self, watchlist_id: str):
        """
        Delete a watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
        """
        self.client.delete_watchlist_by_id(watchlist_id)

    def delete_watchlist_by_name(self, name: str) -> bool:
        """
        Delete a watchlist by name.

        Parameters:
            - name (str) : The watchlist name.
        """
        self.client.delete_watchlist_by_name(name)

    def delete_symbol_from_watchlist(self, watchlist_id: str, symbol: str) -> Optional[Watchlist]:
        """
        Remove a symbol from a specific watchlist.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - symbol (str) : The symbol to remove.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.delete_symbol_from_watchlist(watchlist_id, symbol)

    def add_asset_to_watchlist_by_name(self, name: str, symbol: Optional[str] = None) -> Optional[Watchlist]:
        """
        Add an asset to a watchlist by name.

        Parameters:
            - name (str) : The watchlist name.
            - symbol (str) : The symbol of the asset to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.add_asset_to_watchlist_by_name(name, symbol)

    def add_asset_to_watchlist_by_id(self, watchlist_id: str, symbol: Optional[str] = None) -> Optional[Watchlist]:
        """
        Add an asset to a watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - symbol (str) : The symbol of the asset to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return self.client.add_asset_to_watchlist_by_id(watchlist_id, symbol)

