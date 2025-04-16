# src/algo_royale/client/alpaca_news_client.py
import asyncio
from enum import Enum
import json
import logging
from typing import List, Optional
from models.alpaca_models.alpaca_news import NewsResponse
from datetime import datetime
import httpx
from alpaca.common.enums import Sort
from config.config import ALPACA_PARAMS, ALPACA_SECRETS

class AlpacaNewsClient:
    """Singleton class to interact with Alpaca's API for news data."""
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.api_key = ALPACA_SECRETS["api_key"]
        self.api_secret = ALPACA_SECRETS["api_secret"]
        self.base_url = ALPACA_PARAMS["base_url_data_v1beta1"] 
        self.api_key_header = ALPACA_PARAMS["api_key_header"]
        self.api_secret_header = ALPACA_PARAMS["api_secret_header"]

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)    

        self.subscribed_symbols = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlpacaNewsClient, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def _format_param(self, param):
        if isinstance(param, datetime):
            # Format to ISO 8601 with Zulu time
            return param.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(param, Enum):
            return param.value
        elif isinstance(param, list):
            return ",".join(map(str, param))
        elif isinstance(param, bool):
            return str(param).lower()
        elif param is None:
            return None
        else:
            return str(param)

    def get(
        self,
        url: str,
        includeHeaders: bool = True,
        params: dict = None,
    ):
        """Make a GET request to the Alpaca API."""
        if params is None:
            params = {}
        # Set the headers for authentication

        if includeHeaders:
             headers ={ 
                self.api_key_header: self.api_key,
                self.api_secret_header: self.api_secret}
        else:
            headers = {}
        

        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    

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
                
        responseJson = self.get(
            url=f"{self.base_url}/news",
            params=params
        )

        # self._logger.debug(f"News for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No news data available for {symbols}")
            return None       
        
        return NewsResponse.from_raw(responseJson)


            