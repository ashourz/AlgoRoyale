from datetime import datetime
from typing import Optional

from alpaca.common.enums import Sort, SupportedCurrencies
from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from algo_royale.adapters.market_data.quote_adapter import QuoteAdapter
from algo_royale.models.alpaca_market_data.alpaca_auction import (
    AuctionResponse,
    Auctions,
)
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
from tests.mocks.clients.alpaca.mock_alpaca_stock_client import MockAlpacaStockClient
from tests.mocks.mock_loggable import MockLoggable


class MockQuoteAdapter(QuoteAdapter):
    def __init__(self):
        logger = MockLoggable()
        client = MockAlpacaStockClient()
        super().__init__(alpaca_stock_client=client, logger=logger)
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}
        self.should_return_empty = False
        self.base_quotes_response = QuotesResponse(quotes={}, next_page_token=None)
        self.quote_response = self.base_quotes_response
        self.base_auction_response = AuctionResponse(
            auctions=Auctions(root={}), next_page_token=None
        )
        self.auction_response = self.base_auction_response
        # BarsResponse requires symbol_bars: Dict[str, list[Bar]]
        from algo_royale.models.alpaca_market_data.alpaca_bar import Bar

        dummy_bar = Bar(
            timestamp=datetime.utcnow(),
            open_price=0.0,
            high_price=0.0,
            low_price=0.0,
            close_price=0.0,
            volume=0,
            num_trades=0,
            volume_weighted_price=0.0,
        )
        self.base_bars_response = BarsResponse(
            symbol_bars={"MOCK": [dummy_bar]}, next_page_token=None
        )
        self.bars_response = self.base_bars_response
        self.base_latest_bars_response = LatestBarsResponse(symbol_bars={})
        self.latest_bars_response = self.base_latest_bars_response
        self.base_snapshot_response = SnapshotsResponse(root={})
        self.snapshot_response = self.base_snapshot_response
        self.base_historical_trades_response = HistoricalTradesResponse(
            trades={}, next_page_token=None
        )
        self.historical_trades_response = self.base_historical_trades_response
        self.base_latest_trades_response = LatestTradesResponse(
            trades={}, next_page_token=None
        )
        self.latest_trades_response = self.base_latest_trades_response
        self.base_condition_code_map = ConditionCodeMap(root={})
        self.condition_code_map = self.base_condition_code_map

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_empty(self, value: bool):
        self.should_return_empty = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

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
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.quote_response

    async def fetch_latest_quotes(
        self,
        symbols: list[str],
        currency: SupportedCurrencies = SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[QuotesResponse]:
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        if self.should_return_empty:
            return QuotesResponse(quotes={}, next_page_token=None)
        return self.quote_response

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
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.auction_response

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
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.bars_response

    async def fetch_latest_bars(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[LatestBarsResponse]:
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.latest_bars_response

    async def fetch_condition_codes(
        self, ticktype: TickType, tape: Tape
    ) -> Optional[ConditionCodeMap]:
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.condition_code_map

    async def fetch_snapshots(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: SnapshotFeed = SnapshotFeed.IEX,
    ) -> Optional[SnapshotsResponse]:
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.snapshot_response

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
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.historical_trades_response

    async def fetch_latest_trades(
        self,
        symbols: list[str],
        currency=SupportedCurrencies.USD,
        feed: DataFeed = DataFeed.IEX,
    ) -> Optional[LatestTradesResponse]:
        if self.should_raise:
            raise ValueError("API error")
        if self.should_return_none:
            return None
        return self.latest_trades_response
