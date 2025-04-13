## client\alpaca_api_client.py
import asyncio
from decimal import Decimal
from enum import Enum
import logging
from typing import List, Optional
from models.alpaca_models.alpaca_quote import Quote, QuotesResponse
import pandas as pd
from datetime import datetime
import httpx


from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies

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
        
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)    

        # self.historical_data_client = StockHistoricalDataClient(
        #     api_key=self.api_key,
        #     secret_key=self.api_secret,
        # )
        # self.stock_stream = StockDataStream(
        #     api_key=self.api_key,
        #     secret_key=self.api_secret
        # )

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
    
    # def fetch_latest_quotes(
    #     self,
    #     symbols: List[str],
    #     currency=SupportedCurrencies.USD,
    #     feed: DataFeed = DataFeed.IEX
    # ) -> pd.DataFrame:
    #     """Fetch latest stock quotes from Alpaca."""
        
    #     request = StockLatestQuoteRequest(
    #         symbol_or_symbols = symbols,
    #         feed = feed,
    #         currency = currency
    #     )   

    #     latest_quote = self.historical_data_client.get_stock_latest_quote(request)
    #     self._logger.debug(f"Latest quote for {symbols}: {latest_quote}")
    #     if latest_quote is None:
    #         self._logger.warning(f"No latest quote data available for {symbols}")
    #         return pd.DataFrame()

    #     return latest_quote.df.reset_index()
    
    # def fetch_latest_quote(
    #     self,
    #     symbol: str,
    #     currency=SupportedCurrencies.USD,
    #     feed: DataFeed = DataFeed.IEX
    # ) -> pd.DataFrame:
    #     """Fetch latest stock quotes from Alpaca."""
        
    #     request = StockLatestQuoteRequest(
    #         symbol_or_symbols = symbol,
    #         feed = feed,
    #         currency = currency
    #     )
    #     latest_quote = self.historical_data_client.get_stock_latest_quote(request)
    #     self._logger.debug(f"Latest quote for {symbol}: {latest_quote}")
    #     if latest_quote is None:
    #         self._logger.warning(f"No latest quote data available for {symbols}")
    #         return pd.DataFrame()

    #     return latest_quote.df.reset_index()
  
    async def _subscribe_to_quote_stream(
        self,
        symbols: List[str],
        on_quote: callable = None
    ):
        """Subscribe to Alpaca's real-time quote data stream."""
        async with self._lock:
            try:
                # Ensure the symbols are not already subscribed
                for symbol in symbols:
                    if symbol in self.subscribed_symbols:
                        self._logger.info(f"Already subscribed to {symbol}")
                        continue
                    
                    # Subscribe to the quote stream for each symbol
                    self.stock_stream.subscribe_quotes(on_quote, [symbol])  # Subscribe each symbol separately
                    self._logger.info(f"Subscribed to {symbol}")
                    # Add to the set of subscribed symbols
                    self.subscribed_symbols.add(symbol)  
                self.stock_stream.run()  # Start streaming
            except Exception as e:
                self._logger.error(f"Error subscribing to quote stream: {e}")
            
    def subscribe_quotes(
        self,
        symbols: List[str],
        on_quote: callable = None
    ):
        """Public sync wrapper for async stream subscription."""
        asyncio.run(self._subscribe_to_quote_stream(symbols, on_quote))
        
    async def _unsubscribe_from_quote_stream(self, symbols: List[str]):
        """Unsubscribe from Alpaca's real-time quote data stream."""
        async with self._lock:
            try:
                for symbol in symbols:
                    if symbol not in self.subscribed_symbols:
                        self._logger.info(f"Not subscribed to {symbol}")
                        continue
        
                    # Unsubscribe from the quote stream
                    self.stock_stream.unsubscribe_quotes([symbol])  # Unsubscribe each symbol separately
                    self._logger.info(f"Unsubscribed from {symbol}")
                    self.subscribed_symbols.discard([symbol])  # Remove from subscribed symbols
            except Exception as e:
                self._logger.error(f"Error unsubscribing from quote stream: {e}")
    
    def unsubscribe_quotes(self, symbols: List[str]):
        """Public sync wrapper for async stream unsubscription."""
        asyncio.run(self._unsubscribe_from_quote_stream(symbols))
    
    async def _unsubscribe_all(self):
        """Unsubscribe from all streams."""
        async with self._lock:
            try:
                if not self.subscribed_symbols:
                    self._logger.info("No symbols to unsubscribe from.")
                    return
                self.stock_stream.unsubscribe_all()
                self._logger.info("Unsubscribed from all streams.")
                # Clear the set of subscribed symbols
                self.subscribed_symbols.clear()
            except Exception as e:
                self._logger.error(f"Error unsubscribing from all streams: {e}")

    def unsubscribe_all_quotes(self):
        """Public sync wrapper for async unsubscribe all."""
        asyncio.run(self._unsubscribe_all())
        
    async def _close_stream(self):
        """Close the Alpaca data stream."""
        async with self._lock:
            try:
                if not self.stock_stream.is_running():
                    self._logger.info("Stream is not running.")
                    return
                await self.stock_stream.stop()
                self._logger.info("Stream stopped.")
                await self.stock_stream.close()
                self._logger.info("Stream closed.")
                # Clear the set of subscribed symbols
                self.subscribed_symbols.clear()
                
            except Exception as e:
                self._logger.error(f"Error closing stream: {e}")

            
    def close_stream(self):
        """Public sync wrapper for async stream close."""
        asyncio.run(self._close_stream())
            