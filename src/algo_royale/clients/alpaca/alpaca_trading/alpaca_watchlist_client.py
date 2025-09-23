## client\alpaca_trading\alpaca_watchlist_client.py

from typing import Optional

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.exceptions import (
    AlpacaResourceNotFoundException,
    AlpacaWatchlistNotFoundException,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_watchlist import (
    Watchlist,
    WatchlistListResponse,
)


class AlpacaWatchlistClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for watchlist data."""

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
        return "AlpacaWatchlistClient"

    async def fetch_all_watchlists(self) -> Optional[WatchlistListResponse]:
        """
        Gets all watchlists for an account.
        """

        response = await self.get(
            endpoint="watchlists",
        )

        return WatchlistListResponse.from_raw(response)

    async def fetch_watchlist_by_id(
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
            self.logger.error(
                f"Watchlist not found. Code:{e.status_code} | Message:{e.message}"
            )
            raise AlpacaWatchlistNotFoundException(e.message)

    async def fetch_watchlist_by_name(
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

        response = await self.get(endpoint="watchlists:by_name", params=params)

        return Watchlist.from_raw(response)

    async def delete_watchlist_by_name(
        self,
        name: str,
    ):
        """
        Delete watchlist by client order name.

        Parameters:
            - name (str) :The watchlist name.

        """

        params = {"name": name}

        try:
            await self.delete(endpoint="watchlists:by_name", params=params)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(
                f"Watchlist not found. Code:{e.status_code} | Message:{e.message}"
            )
            raise AlpacaWatchlistNotFoundException(e.message)

    async def delete_symbol_from_watchlist(
        self, watchlist_id: str, symbol: str
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
            response = await self.delete(endpoint=f"watchlists/{watchlist_id}/{symbol}")
            return Watchlist.from_raw(response)
        except AlpacaResourceNotFoundException as e:
            self.logger.error(
                f"Watchlist not found. Code:{e.status_code} | Message:{e.message}"
            )
            raise AlpacaWatchlistNotFoundException(e.message)

    async def update_watchlist_by_id(
        self, watchlist_id: str, name: str
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

        response = await self.put(endpoint=f"watchlists/{watchlist_id}", data=payload)

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
            endpoint="watchlists:by_name", params=params, data=payload
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
            endpoint="watchlists:by_name", params=params, data=payload
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

        response = await self.post(endpoint=f"watchlists/{watchlist_id}", data=payload)

        return Watchlist.from_raw(response)

    async def create_watchlist(
        self,
        name: str,
        symbols: Optional[list[str]],
    ) -> Optional[Watchlist]:
        """
        Create watchlist.

        Parameters:
            - name (str) :The watchlist name.
            - symbols (list[str]) :optional list of symbols to add

        Returns:
            - Watchlist object or None if no response.
        """

        payload = {}
        payload["name"] = name
        if symbols:
            payload["symbols"] = symbols

        response = await self.post(endpoint="watchlists", data=payload)

        return Watchlist.from_raw(response)
