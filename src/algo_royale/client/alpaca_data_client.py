## client\alpaca_api_client.py
import asyncio
from decimal import Decimal
from enum import Enum
import json
import logging
from typing import List, Optional
from models.alpaca_models.alpaca_quote import Quote, QuotesResponse
import pandas as pd
from datetime import datetime
import httpx

from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies
import websockets

from config.config import ALPACA_PARAMS

class AlpacaDataClient:
    """Singleton class to interact with Alpaca's API for stock data."""
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.api_key = ALPACA_PARAMS["api_key"]
        self.api_secret = ALPACA_PARAMS["api_secret"]
        self.base_url = ALPACA_PARAMS["base_url_data"] 
        self.api_key_header = ALPACA_PARAMS["api_key_header"]
        self.api_secret_header = ALPACA_PARAMS["api_secret_header"]
        self.base_url_data_stream = ALPACA_PARAMS["base_url_data_stream_test"]

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)    

        self.subscribed_symbols = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlpacaDataClient, cls).__new__(cls)
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
    

    def fetch_historical_quotes(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        feed: DataFeed = DataFeed.IEX,
        page_limit: int = 1000,
        page_token: str = None,
    ) -> Optional[QuotesResponse]:
        """Fetch historical stock data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")  
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "currency": currency,
            "sort": sort_order,
            "limit": page_limit,
            "page_token": page_token,
            "feed": feed,
            "asof": None,
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self.get(
            url=f"{self.base_url}/stocks/quotes",
            params=params
        )

        self._logger.debug(f"Historical quotes for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No historical data available for {symbols}")
            return None       
        
        return QuotesResponse.from_raw(responseJson)
    
    def fetch_latest_quotes(
        self,
        symbols: List[str],
        currency: SupportedCurrencies =SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[QuotesResponse]:
        """Fetch latest stock quotes from Alpaca."""
        

        if not isinstance(symbols, list):
            symbols = [symbols]
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self.get(
            url=f"{self.base_url}/stocks/quotes/latest",
            params=params
        )

        self._logger.debug(f"Latest quotes for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No latest data available for {symbols}")
            return None       
        
        return QuotesResponse.from_raw(responseJson)

            