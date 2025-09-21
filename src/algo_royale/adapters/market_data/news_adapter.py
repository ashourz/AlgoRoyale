# src/algo_royale/service/alpaca_news_service.py

from datetime import datetime
from typing import Optional, Union

from alpaca.common.enums import Sort

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_news import NewsResponse


class NewsAdapter:
    """
    Service class to interact with Alpaca's NewsClient and
    provide higher-level business logic if needed.
    """

    def __init__(self, client: AlpacaNewsClient, logger: Loggable):
        """
        Initialize the NewsAdapter with the AlpacaNewsClient and a logger.

        Args:
            client (AlpacaNewsClient): Instance of AlpacaNewsClient for API calls.
            logger (Loggable): Logger instance for logging events and errors.
        """
        self.client = client
        self.logger = logger

    async def get_recent_news(
        self,
        symbols: Union[str, list[str]],
        limit: int = 10,
        include_content: bool = True,
        exclude_contentless: bool = True,
        sort_order: Sort = Sort.DESC,
    ) -> Optional[NewsResponse]:
        """
        Fetch recent news articles for a given symbol or list of symbols.
        Returns up to `limit` results.
        """
        return await self.client.async_fetch_news(
            symbols=symbols,
            include_content=include_content,
            exclude_contentless=exclude_contentless,
            sort_order=sort_order,
            page_limit=limit,
        )

    async def get_news_in_date_range(
        self,
        symbols: Union[str, list[str]],
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> Optional[NewsResponse]:
        """
        Fetch news articles for the given symbol(s) between start and end dates.
        """
        return await self.client.async_fetch_news(
            symbols=symbols, start_date=start_date, end_date=end_date, page_limit=limit
        )
