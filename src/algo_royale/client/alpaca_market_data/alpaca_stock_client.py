# src/algo_royale/client/alpaca_quote_client.py

from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_market_data.alpaca_auction import AuctionResponse
from models.alpaca_market_data.alpaca_bar import BarsResponse, LatestBarsResponse
from models.alpaca_market_data.alpaca_condition_code import ConditionCodeMap
from models.alpaca_market_data.alpaca_quote import QuotesResponse
from datetime import datetime

from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from models.alpaca_market_data.alpaca_snapshot import SnapshotsResponse
from models.alpaca_market_data.alpaca_trade import HistoricalTradesResponse, LatestTradesResponse
from models.alpaca_market_data.enums import SnapshotFeed, Tape, TickType

from config.config import ALPACA_PARAMS

    
class AlpacaStockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock data."""
        
    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaStockClient"
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_PARAMS["base_url_data_v2"] 
    
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
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/quotes",
            params=params
        ).json()

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
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/quotes/latest",
            params=params
        ).json()

        self._logger.debug(f"Latest quotes for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No latest data available for {symbols}")
            return None       
        
        return QuotesResponse.from_raw(responseJson)

    def fetch_historical_auctions(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: str = None,
    ) -> Optional[AuctionResponse]:
        """Fetch historical auction data from Alpaca."""

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
            "limit": min(page_limit, 1000),
            "page_token": page_token,
            "feed": DataFeed.SIP,
            "asof": None,
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/auctions",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No auctions data available for {symbols}")
            return None       
        
        return AuctionResponse.from_raw(responseJson)
    
    def fetch_historical_bars(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
        timeframe: TimeFrame = TimeFrame(1, TimeFrameUnit.Minute),
        adjustment: Adjustment = Adjustment.RAW,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: str = None,
    ) -> Optional[BarsResponse]:
        """Fetch historical auction data from Alpaca."""

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
            "feed": feed,
            "timeframe":timeframe,
            "adjustment":adjustment,
            "sort": sort_order,
            "limit": min(page_limit, 1000),
            "page_token": page_token,
            "asof": None,
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/bars",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No auctions data available for {symbols}")
            return None       
        
        return BarsResponse.from_raw(responseJson)
    
    def fetch_latest_bars(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestBarsResponse]:
        """Fetch historical auction data from Alpaca."""

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
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/bars/latest",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No auctions data available for {symbols}")
            return None       
        
        return LatestBarsResponse.from_raw(responseJson)

    def fetch_condition_codes(
        self,
        ticktype: TickType,
        tape: Tape
    ) -> Optional[ConditionCodeMap]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""
        
        params = {}
        for k, v in {
            "tape": tape
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/meta/conditions/{ticktype.value}",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No condition codes data available for {tape}")
            return None       
        
        return ConditionCodeMap.from_raw(responseJson)
    
    
    def fetch_snapshots(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: SnapshotFeed = SnapshotFeed.IEX
    ) -> Optional[SnapshotsResponse]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed        
        }.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/snapshots",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No snapshots data available for {symbols}")
            return None       
        
        self._logger.debug(f"condition codes: {responseJson}")

        return SnapshotsResponse.from_raw(responseJson)

    def fetch_historical_trades(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        limit: int = 1000,
        feed: DataFeed = DataFeed.IEX,
        sort_order: Sort = Sort.DESC,
        page_token: Optional[str] = None
    ) -> Optional[HistoricalTradesResponse]:
        """Fetch historical stock trades from Alpaca between the specified dates for given symbols."""
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "currency": currency,
            "limit": min(limit,1000),
            "feed": feed,
            "sort": sort_order,
            "page_token": page_token,
            "asof": None,
        }.items():
            if v is not None:
                params[k] = self._format_param(v)

        responseJson = self._get(
            url=f"{self.base_url}/stocks/trades",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No historical trade data available for {symbols}")
            return None

        self._logger.debug(f"historical trades: {responseJson}")
        
        return HistoricalTradesResponse.from_raw(responseJson)
    
    def fetch_latest_trades(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestTradesResponse]:
        """Fetch historical stock trades from Alpaca between the specified dates for given symbols."""
        
        params = {}
        for k, v in {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed
        }.items():
            if v is not None:
                params[k] = self._format_param(v)

        responseJson = self._get(
            url=f"{self.base_url}/stocks/trades/latest",
            params=params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No latest trade data available for {symbols}")
            return None

        self._logger.debug(f"latest trades: {responseJson}")
        
        return LatestTradesResponse.from_raw(responseJson)
