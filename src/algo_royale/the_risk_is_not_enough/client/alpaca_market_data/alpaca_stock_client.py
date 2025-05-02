## client\alpaca_market_data\alpaca_stock_client.py

from typing import List, Optional
from algo_royale.the_risk_is_not_enough.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.shared.models.alpaca_market_data.alpaca_auction import AuctionResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_bar import BarsResponse, LatestBarsResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_condition_code import ConditionCodeMap
from algo_royale.shared.models.alpaca_market_data.alpaca_quote import QuotesResponse
from datetime import datetime

from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from algo_royale.shared.models.alpaca_market_data.alpaca_snapshot import SnapshotsResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_trade import HistoricalTradesResponse, LatestTradesResponse
from algo_royale.shared.models.alpaca_market_data.enums import SnapshotFeed, Tape, TickType
from algo_royale.the_risk_is_not_enough.config.config import ALPACA_PARAMS


    
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
        
        params = {
            "symbols": ",".join(symbols),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "currency": currency,
            "sort": sort_order,
            "limit": page_limit,
            "page_token": page_token,
            "feed": feed,
            "asof": None,
        }
                
        response = self.get(
            endpoint="stocks/quotes",
            params=params
        )
        
        return QuotesResponse.from_raw(response)
    
    def fetch_latest_quotes(
        self,
        symbols: List[str],
        currency: SupportedCurrencies =SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[QuotesResponse]:
        """Fetch latest stock quotes from Alpaca."""
        
        if not isinstance(symbols, list):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed
        }
                
        response = self.get(
            endpoint="stocks/quotes/latest",
            params=params
        )
        
        return QuotesResponse.from_raw(response)

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
        
        params = {
            "symbols": ",".join(symbols),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "currency": currency,
            "sort": sort_order,
            "limit": min(page_limit, 1000),
            "page_token": page_token,
            "feed": DataFeed.SIP,
            "asof": None,
        }
                
        response = self.get(
            endpoint="stocks/auctions",
            params=params
        )  
        
        return AuctionResponse.from_raw(response)
    
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
        
        params = {
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
        }
                
        response = self.get(
            endpoint="stocks/bars",
            params=params
        )
        
        return BarsResponse.from_raw(response)
    
    def fetch_latest_bars(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestBarsResponse]:
        """Fetch historical auction data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed
        }
                
        response = self.get(
            endpoint="stocks/bars/latest",
            params=params
        )      
        
        return LatestBarsResponse.from_raw(response)

    def fetch_condition_codes(
        self,
        ticktype: TickType,
        tape: Tape
    ) -> Optional[ConditionCodeMap]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""
        
        params = {
            "tape": tape
        }
                
        response = self.get(
            endpoint=f"stocks/meta/conditions/{ticktype.value}",
            params=params
        )
        
        return ConditionCodeMap.from_raw(response)
    
    
    def fetch_snapshots(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: SnapshotFeed = SnapshotFeed.IEX
    ) -> Optional[SnapshotsResponse]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""
        
        params = {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed        
        }
        response = self.get(
            endpoint="stocks/snapshots",
            params=params
        )

        return SnapshotsResponse.from_raw(response)

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
        
        params = {
            "symbols": ",".join(symbols),
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "currency": currency,
            "limit": min(limit,1000),
            "feed": feed,
            "sort": sort_order,
            "page_token": page_token,
            "asof": None,
        }

        response = self.get(
            endpoint="stocks/trades",
            params=params
        )
        
        return HistoricalTradesResponse.from_raw(response)
    
    def fetch_latest_trades(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestTradesResponse]:
        """Fetch historical stock trades from Alpaca between the specified dates for given symbols."""
        
        params = {
            "symbols": ",".join(symbols),
            "currency": currency,
            "feed": feed
        }

        response = self.get(
            endpoint="stocks/trades/latest",
            params=params
        )
        
        return LatestTradesResponse.from_raw(response)
