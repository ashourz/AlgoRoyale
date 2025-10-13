## client\alpaca_market_data\alpaca_news_client.py

from datetime import datetime
from typing import Optional, Union

from alpaca.common.enums import Sort

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_news import NewsResponse


class AlpacaNewsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data."""

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
        return "AlpacaNewsClient"

    async def async_fetch_news(
        self,
        symbols: Optional[Union[str, list[str]]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_content: Optional[bool] = None,
        exclude_contentless: Optional[bool] = None,
        sort_order: Optional[Sort] = None,
        page_limit: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Optional[NewsResponse]:
        """Fetch news data from Alpaca."""

        if symbols is None:
            symbols = []
        if isinstance(symbols, str):
            symbols = [symbols]
        elif not isinstance(symbols, list):
            raise ValueError("symbols must be a list of strings or a single string")

        if start_date is not None and not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object or None")
        if end_date is not None and not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object or None")

        params = {}

        if symbols:
            params["symbols"] = symbols
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
        if include_content is not None:
            params["include_content"] = include_content
        if exclude_contentless is not None:
            params["exclude_contentless"] = exclude_contentless
        if sort_order:
            params["sort"] = sort_order
        if page_limit is not None:
            params["limit"] = min(page_limit, 50)
        if page_token:
            params["page_token"] = page_token

        response = await self.get(endpoint="news", params=params)

        return NewsResponse.from_raw(response)
