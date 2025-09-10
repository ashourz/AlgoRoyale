## client\alpaca_market_data\alpaca_corporate_action_client.py

from datetime import datetime
from typing import Optional

from alpaca.common.enums import Sort

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateActionResponse,
)
from algo_royale.models.alpaca_market_data.enums import CorporateActions


class AlpacaCorporateActionClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for market data corporate action data."""

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
        return "AlpacaCorporateActionClient"

    async def fetch_corporate_actions(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        cusips: list[str] = [],
        types: list[CorporateActions] = [],
        ids: list[str] = [],
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[CorporateActionResponse]:
        """Fetch news data from Alpaca.

        attrs:
            symbols (list[str]): List of stock symbols to fetch news for.
            start_date (datetime): Start date for the news data.
            end_date (datetime): End date for the news data.
            cusips (list[str]): List of CUSIPs to filter by.
            types (list[CorporateActions]): List of corporate action types to filter by.
            ids (list[str]): List of IDs to filter by.
            sort_order (Sort): Sort order for the results. Default is descending.
            page_limit (int): Maximum number of results to return. Default is 1000.
            page_token (str): Token for pagination. Default is None.
        """

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")

        params = {
            "symbols": ",".join(symbols),
            "start": start_date.strftime("%Y-%m-%d"),  # YYYY-MM-DD format
            "end": end_date.strftime("%Y-%m-%d"),  # YYYY-MM-DD format
            "sort": sort_order,
            "limit": min(page_limit, 1000),  # Alpaca limits to 1000
        }
        if cusips:
            params["cusips"] = cusips
        if types:
            params["types"] = types
        if ids:
            params["ids"] = ids
        if page_token is not None:
            params["page_token"] = page_token

        response = await self.get(endpoint="corporate-actions", params=params)

        return CorporateActionResponse.from_raw(response)
