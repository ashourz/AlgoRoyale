# src/algo_royale/client/alpaca_news_client.py

from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_market_data.alpaca_news import NewsResponse
from datetime import datetime
from alpaca.common.enums import Sort
from config.config import ALPACA_PARAMS

class AlpacaNewsClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_PARAMS["base_url_data_v1beta1"] 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaNewsClient"    
    
    def fetch_news(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        include_content: bool = True,
        exclude_contentless: bool = False,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: str = None,
    ) -> Optional[NewsResponse]:
        """Fetch news data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")  
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "start": start_date.strftime("%Y-%m-%d"),  # YYYY-MM-DD format
            "end": end_date.strftime("%Y-%m-%d"),      # YYYY-MM-DD format
            "include_content": include_content,
            "exclude_contentless": exclude_contentless,
            "sort": sort_order,
            "limit": min(page_limit, 50),  # Alpaca limits to 50
            "page_token": page_token,
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/news",
            params=params
        ).json()

        # self._logger.debug(f"News for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No news data available for {symbols}")
            return None       
        
        return NewsResponse.from_raw(responseJson)
