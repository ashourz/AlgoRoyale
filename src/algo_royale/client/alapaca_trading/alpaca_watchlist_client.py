# src/algo_royale/client/alpaca_trading/alpaca_portfolio_client.py

from datetime import date, datetime
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.client.exceptions import ParameterConflictError
from models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from models.alpaca_trading.alpaca_watchlist import Watchlist, WatchlistListResponse
from models.alpaca_trading.enums import IntradayReporting, PNLReset
from config.config import ALPACA_TRADING_URL

class AlpacaWatchlistClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for watchlist data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaWatchlistClient"    
    
    def fetch_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for an account.
         """
                
        responseJson = self._get(
            url=f"{self.base_url}/watchlists",
        ).json()

        if responseJson is None:
            self._logger.warning(f"No watchlist data available")
            return None       
        
        return WatchlistListResponse.from_raw(responseJson)
            
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
                
        response_json = self._get(
            url=f"{self.base_url}/watchlists/{watchlist_id}",
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
    def delete_watchlist_by_id(
        self,
        watchlist_id: str,
    ):
        """
        Get order by client order id.

        Parameters:
            - watchlist_id (str) :The watchlist ID.
        """
                
        response = self._delete(
            url=f"{self.base_url}/watchlists/{watchlist_id}",
        )

        return response
    
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

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._get(
            url=f"{self.base_url}/watchlists:by_name",
            params = params
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
    def delete_watchlist_by_name(
        self,
        name: str,
    ):
        """
        Delete watchlist by client order name.

        Parameters:
            - name (str) :The watchlist name.

        """
                
        params = {"name": name}

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response = self._delete(
            url=f"{self.base_url}/watchlists:by_name",
            params = params
        )

        return response
    
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
        
        response_json = self._delete(
            url=f"{self.base_url}/watchlists/{watchlist_id}/{symbol}"
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
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

        params = {"name": name}

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._post(
            url=f"{self.base_url}/watchlists/{watchlist_id}",
            params = params
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
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

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._post(
            url=f"{self.base_url}/watchlists:by_name",
            params = params,
            payload = payload
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
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

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._post(
            url=f"{self.base_url}/watchlists:by_name",
            params = params,
            payload = payload
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
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

        params = {}
        if symbol:
            params["symbol"] = symbol

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._post(
            url=f"{self.base_url}/watchlists/{watchlist_id}",
            params = params
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)
    
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

        params = {}
        params["name"] = name
        if symbols:
            params["symbols"] = symbols

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._post(
            url=f"{self.base_url}/watchlists",
            params = params
        ).json()

        if response_json is None:
            self._logger.warning("No watchlist response received.")
            return None

        return Watchlist.from_raw(response_json)