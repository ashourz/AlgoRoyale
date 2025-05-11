## client\alpaca_trading\alpaca_watchlist_client.py

from typing import List, Optional
from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.exceptions import AlpacaResourceNotFoundException, AlpacaWatchlistNotFoundException
from algo_royale.models.alpaca_trading.alpaca_watchlist import Watchlist, WatchlistListResponse
from algo_royale.clients.alpaca.alpaca_client_config import ALPACA_TRADING_URL

class AlpacaWatchlistClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for watchlist data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaWatchlistClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL    

    async def get_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for an account.
         """
                
        response = await self.get(
            endpoint="watchlists",
        ) 
        
        return WatchlistListResponse.from_raw(response)
            
    async def get_watchlist_by_id(
        self,
        watchlist_id: str,
    ) -> Optional[Watchlist]:
        """
        Get order by client order id.

        Parameters:
            - watchlist_id (str) :The watchlist ID.

        Returns:
            - Watchlist object or None if no response.
        """
                
        response = await self.get(
            endpoint=f"watchlists/{watchlist_id}",
        )

        return Watchlist.from_raw(response)
    
    async def delete_watchlist_by_id(
        self,
        watchlist_id: str,
    ):
        """
        Get order by client order id.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
        """
        try:
            await self.delete(
                endpoint=f"watchlists/{watchlist_id}",
            )
        except AlpacaResourceNotFoundException as e: 
            self.logger.error(f"Watchlist not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaWatchlistNotFoundException(e.message)
        
    async def get_watchlist_by_name(
        self,
        name: str,
    ) -> Optional[Watchlist]:
        """
        Get watchlist by client order name.

        Parameters:
            - name (str) : The watchlist name.

        Returns:
            - Watchlist object or None if no response.
        """
                
        params = {"name": name}
                
        response = await self.get(
            endpoint="watchlists:by_name",
            params = params
        )

        return Watchlist.from_raw(response)
    
    async def delete_watchlist_by_name(
        self,
        name: str,
    ) -> bool:
        """
        Delete watchlist by client order name.

        Parameters:
            - name (str) :The watchlist name.

        """
                
        params = {"name": name}
        
        try:
            await self.delete(
                endpoint="watchlists:by_name",
                params = params
            )
        except AlpacaResourceNotFoundException as e: 
            self.logger.error(f"Watchlist not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaWatchlistNotFoundException(e.message)
        
    async def delete_symbol_from_watchlist(
        self,
        watchlist_id: str,
        symbol: str
    ) -> Optional[Watchlist]:
        """
        Delete watchlist by client order name.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
            - symbol (str) :The watchlist symbol.

        Returns:
            - Watchlist object or None if no response.
        """
        try:
            response = await self.delete(
                endpoint=f"watchlists/{watchlist_id}/{symbol}"
            )
            return Watchlist.from_raw(response)
        except AlpacaResourceNotFoundException as e: 
            self.logger.error(f"Watchlist not found. Code:{e.status_code} | Message:{e.message}")
            raise AlpacaWatchlistNotFoundException(e.message)
        
    async def update_watchlist_by_id(
        self,
        watchlist_id: str,
        name: str
    ) -> Optional[Watchlist]:
        """
        Update watchlist by id.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
            - name (str) :The watchlist name.

        Returns:
            - Watchlist object or None if no response.
        """

        payload = {"name": name}
                
        response = await self.put(
            endpoint=f"watchlists/{watchlist_id}",
            data = payload
        )
        
        return Watchlist.from_raw(response)
    
    async def update_watchlist_by_name(
        self,
        name: str,
        update_name: str,
    ) -> Optional[Watchlist]:
        """
        Update watchlist by name.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
            - name (str) :The watchlist name.
            - update_name (str) :The updated watchlist name.

        Returns:
            - Watchlist object or None if no response.
        """

        params = {"name": name}
        payload = {"name": update_name}
                
        response = await self.put(
            endpoint="watchlists:by_name",
            params = params,
            data = payload
        )

        return Watchlist.from_raw(response)
    
    async def add_asset_to_watchlist_by_name(
        self,
        name: str,
        symbol: Optional[str],
    ) -> Optional[Watchlist]:
        """
        Update watchlist by name.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
            - name (str) :The watchlist name.
            - symbol (str) :The asset symbol to add.

        Returns:
            - Watchlist object or None if no response.
        """

        params = {"name": name}
        payload = {}
        if symbol:
            params["symbol"] = symbol
                
        response = await self.post(
            endpoint="watchlists:by_name",
            params = params,
            data = payload
        )

        return Watchlist.from_raw(response)
    
    async def add_asset_to_watchlist_by_id(
        self,
        watchlist_id: str,
        symbol: Optional[str],
    ) -> Optional[Watchlist]:
        """
        Update watchlist by name.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
            - symbol (str) :The asset symbol to add.

        Returns:
            - Watchlist object or None if no response.
        """

        payload = {}
        if symbol:
            payload["symbol"] = symbol

                
        response = await self.post(
            endpoint=f"watchlists/{watchlist_id}",
            data = payload
        )

        return Watchlist.from_raw(response)
    
    async def create_watchlist(
        self,
        name: str,
        symbols: Optional[List[str]],
    ) -> Optional[Watchlist]:
        """
        Create watchlist.

        Parameters:
            - name (str) :The watchlist name.
            - symbols (List[str]) :optional list of symbols to add

        Returns:
            - Watchlist object or None if no response.
        """

        payload = {}
        payload["name"] = name
        if symbols:
            payload["symbols"] = symbols
                
        response = await self.post(
            endpoint="watchlists",
            data = payload
        )

        return Watchlist.from_raw(response)