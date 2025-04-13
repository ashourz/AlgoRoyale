## client\alpaca_api_client.py
from decimal import Decimal
from typing import List
import pandas as pd
from datetime import datetime

from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import Sort, SupportedCurrencies

from config.config import ALPACA_PARAMS

class AlpacaClient:
    def __init__(self, use_paper: bool = True):
        self.api_key = ALPACA_PARAMS["api_key"]
        self.api_secret = ALPACA_PARAMS["api_secret"]
        self.base_url = ALPACA_PARAMS["base_url_paper"] if use_paper else ALPACA_PARAMS["base_url_live"]

        self.client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.api_secret,
            url_override=self.base_url
        )

    def fetch_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        timeframe=TimeFrame(1, TimeFrameUnit.Minute),
        sort_order: Sort = Sort.DESC,
        feed: DataFeed = DataFeed.IEX,
        adjustment: Adjustment = Adjustment.RAW
    ) -> pd.DataFrame:
        """Fetch historical stock data from Alpaca."""

        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            start=start_date,
            end=end_date,
            currency=SupportedCurrencies.USD,
            sort=sort_order,
            timeframe=timeframe,
            adjustment=adjustment,
            feed=feed,
            asof=None
        )

        bars = self.client.get_stock_bars(request)
        return bars.df.reset_index()
    
    