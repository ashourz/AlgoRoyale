# src/algo_royale/service/alpaca_watchlist_service.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.models.alpaca_trading.alpaca_watchlist import (
    Watchlist,
    WatchlistListResponse,
)


class AlpacaWatchlistService:
    """Service class for interacting with Alpaca's watchlist data."""

    def __init__(self, client: AlpacaWatchlistClient):
        self.client = client

    async def get_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for the account.

        Returns:
            - WatchlistListResponse object or None if no response.
        """
        return await self.client.get_all_watchlists()

    async def get_watchlist_by_id(self, watchlist_id: str) -> Optional[Watchlist]:
        """
        Get a specific watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.get_watchlist_by_id(watchlist_id)

    async def get_watchlist_by_name(self, name: str) -> Optional[Watchlist]:
        """
        Get a specific watchlist by name.

        Parameters:
            - name (str) : The watchlist name.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.get_watchlist_by_name(name)

    async def create_watchlist(
        self, name: str, symbols: Optional[list[str]] = None
    ) -> Optional[Watchlist]:
        """
        Create a new watchlist.

        Parameters:
            - name (str) : The name of the watchlist.
            - symbols (list[str]) : Optional list of symbols to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.create_watchlist(name, symbols)

    async def update_watchlist_by_id(
        self, watchlist_id: str, name: str
    ) -> Optional[Watchlist]:
        """
        Update an existing watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - name (str) : The new name of the watchlist.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.update_watchlist_by_id(watchlist_id, name)

    async def update_watchlist_by_name(
        self, name: str, update_name: str
    ) -> Optional[Watchlist]:
        """
        Update an existing watchlist by name.

        Parameters:
            - name (str) : The original name of the watchlist.
            - update_name (str) : The new name of the watchlist.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.update_watchlist_by_name(name, update_name)

    async def delete_watchlist_by_id(self, watchlist_id: str):
        """
        Delete a watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
        """
        await self.client.delete_watchlist_by_id(watchlist_id)

    async def delete_watchlist_by_name(self, name: str) -> bool:
        """
        Delete a watchlist by name.

        Parameters:
            - name (str) : The watchlist name.
        """
        await self.client.delete_watchlist_by_name(name)

    async def delete_symbol_from_watchlist(
        self, watchlist_id: str, symbol: str
    ) -> Optional[Watchlist]:
        """
        Remove a symbol from a specific watchlist.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - symbol (str) : The symbol to remove.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.delete_symbol_from_watchlist(watchlist_id, symbol)

    async def add_asset_to_watchlist_by_name(
        self, name: str, symbol: Optional[str] = None
    ) -> Optional[Watchlist]:
        """
        Add an asset to a watchlist by name.

        Parameters:
            - name (str) : The watchlist name.
            - symbol (str) : The symbol of the asset to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.add_asset_to_watchlist_by_name(name, symbol)

    async def add_asset_to_watchlist_by_id(
        self, watchlist_id: str, symbol: Optional[str] = None
    ) -> Optional[Watchlist]:
        """
        Add an asset to a watchlist by ID.

        Parameters:
            - watchlist_id (str) : The watchlist ID.
            - symbol (str) : The symbol of the asset to add.

        Returns:
            - Watchlist object or None if no response.
        """
        return await self.client.add_asset_to_watchlist_by_id(watchlist_id, symbol)
