# src/algo_royale/client/alpaca_quote_client.py

from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_models.alpaca_auction import AuctionResponse
from models.alpaca_models.alpaca_bar import BarsResponse, LatestBarsResponse
from models.alpaca_models.alpaca_condition_code import ConditionCodeMap
from models.alpaca_models.alpaca_quote import QuotesResponse
from datetime import datetime

from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from models.alpaca_models.alpaca_snapshot import SnapshotsResponse

from config.config import ALPACA_PARAMS


class TickType(Enum):
        TRADE = "trade"
        QUOTE = "quote"
    
class Tape(Enum):
    A = "A",
    B = "B",
    C = "C"

class SnapshotFeed(Enum):
    DELAYED_SIP = "delayed_sip",
    IEX = "iex",
    OTC = "otc",
    SIP = "sip"
    
class AlpacaStockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock data."""
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_PARAMS["base_url_data_v2"] 
        
    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaStockClient"
    

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
                
        responseJson = self._get(
            url=f"{self.base_url}/stocks/quotes/latest",
            params=params
        )

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
        )

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
        )

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
        )

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
        )

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
        )

        if responseJson is None:
            self._logger.warning(f"No snapshots data available for {symbols}")
            return None       
        
        self._logger.debug(f"condition codes: {responseJson}")

        return SnapshotsResponse.from_raw(responseJson)
    