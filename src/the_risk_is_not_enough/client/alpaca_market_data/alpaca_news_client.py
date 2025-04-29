## client\alpaca_market_data\alpaca_news_client.py

from enum import Enum
from typing import List, Optional, Union
from the_risk_is_not_enough.client.alpaca_base_client import AlpacaBaseClient
from shared.models.alpaca_market_data.alpaca_news import NewsResponse
from datetime import datetime
from alpaca.common.enums import Sort
from config.config import ALPACA_PARAMS

class AlpacaNewsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaNewsClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_PARAMS["base_url_data_v1beta1"] 
    
    def fetch_news(
        self,
        symbols: Optional[Union[str, List[str]]] = None,
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

        response = self.get(
            endpoint=f"news",
            params=params
        )

        return NewsResponse.from_raw(response)