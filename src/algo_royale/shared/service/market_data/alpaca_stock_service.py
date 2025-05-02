# src/algo_royale/service/alpaca_quote_service.py

from datetime import datetime
from typing import List, Optional

from algo_royale.the_risk_is_not_enough.client.alpaca_market_data.alpaca_stock_client import AlpacaStockClient
from algo_royale.shared.models.alpaca_market_data.alpaca_auction import AuctionResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_bar import BarsResponse, LatestBarsResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_condition_code import ConditionCodeMap
from algo_royale.shared.models.alpaca_market_data.alpaca_quote import QuotesResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_snapshot import SnapshotsResponse
from algo_royale.shared.models.alpaca_market_data.alpaca_trade import HistoricalTradesResponse, LatestTradesResponse
from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from algo_royale.shared.models.alpaca_market_data.enums import SnapshotFeed, Tape, TickType


class AlpacaQuoteService:
    """
    Service class to interact with Alpaca's API for retrieving market data such as quotes, trades, auctions, and bars.
    This class abstracts the AlpacaStockClient and provides higher-level methods to fetch data.
    """

    def __init__(self):
        self.client = AlpacaStockClient()

    def fetch_historical_quotes(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        feed: DataFeed = DataFeed.IEX,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[QuotesResponse]:
        """
        Fetch historical stock data from Alpaca for the given symbols and date range.
        
        Parameters:
            symbols (List[str]): List of stock symbols to query.
            start_date (datetime): Start date for the historical data.
            end_date (datetime): End date for the historical data.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            sort_order (Sort): Sort order for the data.
            feed (DataFeed): Data feed provider.
            page_limit (int): Maximum number of records to return.
            page_token (Optional[str]): Pagination token for fetching next pages of results.

        Returns:
            Optional[QuotesResponse]: Historical stock quotes if successful.
        """
        return self.client.fetch_historical_quotes(
            symbols, start_date, end_date, currency, sort_order, feed, page_limit, page_token
        )
    
    def fetch_latest_quotes(
        self,
        symbols: List[str],
        currency: SupportedCurrencies = SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[QuotesResponse]:
        """
        Fetch the latest stock quotes for the given symbols from Alpaca.

        Parameters:
            symbols (List[str]): List of stock symbols.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            feed (DataFeed): Data feed provider.

        Returns:
            Optional[QuotesResponse]: Latest stock quotes if successful.
        """
        return self.client.fetch_latest_quotes(symbols, currency, feed)

    def fetch_historical_auctions(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        currency=SupportedCurrencies.USD,
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Optional[AuctionResponse]:
        """
        Fetch historical auction data from Alpaca for the given symbols and date range.

        Parameters:
            symbols (List[str]): List of stock symbols to query.
            start_date (datetime): Start date for the historical auctions.
            end_date (datetime): End date for the historical auctions.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            sort_order (Sort): Sort order for the auction data.
            page_limit (int): Maximum number of records to return.
            page_token (Optional[str]): Pagination token for fetching next pages of results.

        Returns:
            Optional[AuctionResponse]: Historical auction data if successful.
        """
        return self.client.fetch_historical_auctions(
            symbols, start_date, end_date, currency, sort_order, page_limit, page_token
        )

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
        page_token: Optional[str] = None,
    ) -> Optional[BarsResponse]:
        """
        Fetch historical bar data for the given symbols and date range.

        Parameters:
            symbols (List[str]): List of stock symbols.
            start_date (datetime): Start date for the historical bars.
            end_date (datetime): End date for the historical bars.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            feed (DataFeed): Data feed provider.
            timeframe (TimeFrame): The timeframe for the bars.
            adjustment (Adjustment): The adjustment for the bars.
            sort_order (Sort): Sort order for the data.
            page_limit (int): Maximum number of records to return.
            page_token (Optional[str]): Pagination token for fetching next pages of results.

        Returns:
            Optional[BarsResponse]: Historical bar data if successful.
        """
        return self.client.fetch_historical_bars(
            symbols, start_date, end_date, currency, feed, timeframe, adjustment, sort_order, page_limit, page_token
        )

    def fetch_latest_bars(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestBarsResponse]:
        """
        Fetch the latest bar data for the given symbols from Alpaca.

        Parameters:
            symbols (List[str]): List of stock symbols.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            feed (DataFeed): Data feed provider.

        Returns:
            Optional[LatestBarsResponse]: Latest bar data if successful.
        """
        return self.client.fetch_latest_bars(symbols, currency, feed)

    def fetch_condition_codes(
        self,
        ticktype: TickType,
        tape: Tape
    ) -> Optional[ConditionCodeMap]:
        """
        Fetch condition code metadata for a specific tick type and tape.

        Parameters:
            ticktype (TickType): The type of the tick.
            tape (Tape): The tape for the stock.

        Returns:
            Optional[ConditionCodeMap]: Condition code map if successful.
        """
        return self.client.fetch_condition_codes(ticktype, tape)

    def fetch_snapshots(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: SnapshotFeed = SnapshotFeed.IEX
    ) -> Optional[SnapshotsResponse]:
        """
        Fetch snapshot data for the given symbols.

        Parameters:
            symbols (List[str]): List of stock symbols.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            feed (SnapshotFeed): Data feed provider.

        Returns:
            Optional[SnapshotsResponse]: Snapshot data if successful.
        """
        return self.client.fetch_snapshots(symbols, currency, feed)

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
        """
        Fetch historical trade data for the given symbols and date range.

        Parameters:
            symbols (List[str]): List of stock symbols.
            start_date (datetime): Start date for the historical trades.
            end_date (datetime): End date for the historical trades.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            limit (int): Maximum number of trades to return.
            feed (DataFeed): Data feed provider.
            sort_order (Sort): Sort order for the data.
            page_token (Optional[str]): Pagination token for fetching next pages of results.

        Returns:
            Optional[HistoricalTradesResponse]: Historical trade data if successful.
        """
        return self.client.fetch_historical_trades(
            symbols, start_date, end_date, currency, limit, feed, sort_order, page_token
        )

    def fetch_latest_trades(
        self,
        symbols: List[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX
    ) -> Optional[LatestTradesResponse]:
        """
        Fetch the latest trade data for the given symbols from Alpaca.

        Parameters:
            symbols (List[str]): List of stock symbols.
            currency (SupportedCurrencies): The currency in which the data should be returned.
            feed (DataFeed): Data feed provider.

        Returns:
            Optional[LatestTradesResponse]: Latest trade data if successful.
        """
        return self.client.fetch_latest_trades(symbols, currency, feed)
