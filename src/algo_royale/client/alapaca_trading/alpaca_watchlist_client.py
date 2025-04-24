# src/algo_royale/client/alpaca_trading/alpaca_portfolio_client.py

from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_watchlist import Watchlist, WatchlistListResponse
from config.config import ALPACA_TRADING_URL

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

    def get_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for an account.
         """
                
        response = self.get(
            endpoint=f"{self.base_url}/watchlists",
        ) 
        
        return WatchlistListResponse.from_raw(response)
            
    def get_watchlist_by_id(
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
                
        response = self._get(
            endpoint=f"{self.base_url}/watchlists/{watchlist_id}",
        )

        return Watchlist.from_raw(response)
    
    def delete_watchlist_by_id(
        self,
        watchlist_id: str,
    ):
        """
        Get order by client order id.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
        """
                
        self.delete(
            endpoint=f"{self.base_url}/watchlists/{watchlist_id}",
        )
    
    def get_watchlist_by_name(
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
                
        response = self.get(
            endpoint=f"{self.base_url}/watchlists:by_name",
            params = params
        )

        return Watchlist.from_raw(response)
    
    def delete_watchlist_by_name(
        self,
        name: str,
    ) -> bool:
        """
        Delete watchlist by client order name.

        Parameters:
            - name (str) :The watchlist name.

        """
                
        params = {"name": name}
                
        self.delete(
            endpoint=f"{self.base_url}/watchlists:by_name",
            params = params
        )

    def delete_symbol_from_watchlist(
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
        
        response = self._delete(
            endpoint=f"{self.base_url}/watchlists/{watchlist_id}/{symbol}"
        )

        return Watchlist.from_raw(response)
    
    def update_watchlist_by_id(
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
                
        response = self.put(
            endpoint=f"{self.base_url}/watchlists/{watchlist_id}",
            payload = payload
        )
        
        return Watchlist.from_raw(response)
    
    def update_watchlist_by_name(
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
                
        response = self.put(
            endpoint=f"{self.base_url}/watchlists:by_name",
            params = params,
            payload = payload
        )

        return Watchlist.from_raw(response)
    
    def add_asset_to_watchlist_by_name(
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
                
        response = self.post(
            endpoint=f"{self.base_url}/watchlists:by_name",
            params = params,
            payload = payload
        )

        return Watchlist.from_raw(response)
    
    def add_asset_to_watchlist_by_id(
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

                
        response = self.post(
            endpoint=f"{self.base_url}/watchlists/{watchlist_id}",
            payload = payload
        )

        return Watchlist.from_raw(response)
    
    def create_watchlist(
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
                
        response = self.post(
            endpoint=f"{self.base_url}/watchlists",
            payload = payload
        )

        return Watchlist.from_raw(response)