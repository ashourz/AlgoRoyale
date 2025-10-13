## client\alpaca_market_data\alpaca_stock_client.py

from datetime import datetime
from typing import Optional

from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_auction import AuctionResponse
from algo_royale.models.alpaca_market_data.alpaca_bar import (
    BarsResponse,
    LatestBarsResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_condition_code import ConditionCodeMap
from algo_royale.models.alpaca_market_data.alpaca_quote import QuotesResponse
from algo_royale.models.alpaca_market_data.alpaca_snapshot import SnapshotsResponse
from algo_royale.models.alpaca_market_data.alpaca_trade import (
    HistoricalTradesResponse,
    LatestTradesResponse,
)
from algo_royale.models.alpaca_market_data.enums import SnapshotFeed, Tape, TickType


class AlpacaStockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for stock data."""

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
        return "AlpacaStockClient"

    async def fetch_historical_quotes(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        feed: DataFeed = DataFeed.IEX,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[QuotesResponse]:
        """Fetch historical stock data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        params = {
            "symbols": ",".join(symbols),
            "start": start_str,
            "end": end_str,
            "currency": currency,
            "sort": sort_order,
            "limit": page_limit,
            "page_token": page_token,
            "feed": feed,
            "asof": None,
        }

        response = await self.get(endpoint="stocks/quotes", params=params)

        return QuotesResponse.from_raw(response)

    async def fetch_latest_quotes(
        self,
        symbols: list[str],
        currency: SupportedCurrencies = SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[QuotesResponse]:
        """Fetch latest stock quotes from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]

        params = {"symbols": ",".join(symbols), "currency": currency, "feed": feed}

        response = await self.get(endpoint="stocks/quotes/latest", params=params)

        return QuotesResponse.from_raw(response)

    async def fetch_historical_auctions(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[AuctionResponse]:
        """Fetch historical auction data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        params = {
            "symbols": ",".join(symbols),
            "start": start_str,
            "end": end_str,
            "currency": currency,
            "sort": sort_order,
            "limit": min(page_limit, 1000),
            "page_token": page_token,
            "feed": DataFeed.SIP,
            "asof": None,
        }

        response = await self.get(endpoint="stocks/auctions", params=params)

        return AuctionResponse.from_raw(response)

    async def fetch_historical_bars(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
        timeframe: TimeFrame = TimeFrame(1, TimeFrameUnit.Minute),
        adjustment: Adjustment = Adjustment.RAW,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[BarsResponse]:
        """Fetch historical auction data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        params = {
            "symbols": ",".join(symbols),
            "start": start_str,
            "end": end_str,
            "currency": currency,
            "feed": feed,
            "timeframe": timeframe,
            "adjustment": adjustment,
            "sort": sort_order,
            "limit": min(page_limit, 1000),
            "page_token": page_token,
            "asof": None,
        }

        response = await self.get(endpoint="stocks/bars", params=params)

        return BarsResponse.from_raw(response)

    async def fetch_latest_bars(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[LatestBarsResponse]:
        """Fetch historical auction data from Alpaca."""

        if not isinstance(symbols, list):
            symbols = [symbols]

        params = {"symbols": ",".join(symbols), "currency": currency, "feed": feed}

        response = await self.get(endpoint="stocks/bars/latest", params=params)

        return LatestBarsResponse.from_raw(response)

    async def fetch_condition_codes(
        self, ticktype: TickType, tape: Tape
    ) -> Optional[ConditionCodeMap]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""

        params = {"tape": tape}

        response = await self.get(
            endpoint=f"stocks/meta/conditions/{ticktype.value}", params=params
        )

        return ConditionCodeMap.from_raw(response)

    async def fetch_snapshots(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: SnapshotFeed = SnapshotFeed.IEX,
    ) -> Optional[SnapshotsResponse]:
        """Fetch condition codes metadata from Alpaca for a specific tick type and tape."""

        params = {"symbols": ",".join(symbols), "currency": currency, "feed": feed}
        response = await self.get(endpoint="stocks/snapshots", params=params)

        return SnapshotsResponse.from_raw(response)

    async def fetch_historical_trades(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        limit: int = 1000,
        feed: DataFeed = DataFeed.IEX,
        sort_order: Sort = Sort.DESC,
        page_token: Optional[str] = None,
    ) -> Optional[HistoricalTradesResponse]:
        """Fetch historical stock trades from Alpaca between the specified dates for given symbols."""
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        params = {
            "symbols": ",".join(symbols),
            "start": start_str,
            "end": end_str,
            "currency": currency,
            "limit": min(limit, 1000),
            "feed": feed,
            "sort": sort_order,
            "page_token": page_token,
            "asof": None,
        }

        response = await self.get(endpoint="stocks/trades", params=params)

        return HistoricalTradesResponse.from_raw(response)

    async def fetch_latest_trades(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[LatestTradesResponse]:
        """Fetch historical stock trades from Alpaca between the specified dates for given symbols."""

        params = {"symbols": ",".join(symbols), "currency": currency, "feed": feed}

        response = await self.get(endpoint="stocks/trades/latest", params=params)

        return LatestTradesResponse.from_raw(response)
