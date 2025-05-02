from datetime import datetime
import os
import pandas as pd
from shared.models.alpaca_market_data.enums import DataFeed
from shared.service.market_data.alpaca_stock_service import AlpacaQuoteService
from trade_another_day.config.config import load_config
from trade_another_day.utils.watchlist import load_watchlist
from alpaca.common.enums import SupportedCurrencies

class BacktestDataLoader:
    def __init__(self):
        self.config = load_config()
        self.data_dir = self.config["data_dir"]
        os.makedirs(self.data_dir, exist_ok=True)
        self.quote_client = AlpacaQuoteService()
        self.watchlist = load_watchlist(self.config["watchlist_path"])
        self.start_date = datetime.strptime(self.config["start_date"], "%Y-%m-%d")
        self.end_date =  datetime.strptime(self.config["end_date"], "%Y-%m-%d")
        self.interval =  self.config["interval"]

    def load_all(self, fetch_if_missing=True) -> dict:
        """
        Loads data for all symbols in the watchlist.
        Returns a dict of {symbol: DataFrame}
        """
        data = {}
        for symbol in self.watchlist:
            try:
                data[symbol] = self.load_symbol(symbol, fetch_if_missing)
            except Exception as e:
                print(f"[WARN] Could not load data for {symbol}: {e}")
        return data

    def load_symbol(self, symbol: str, fetch_if_missing=True) -> pd.DataFrame:
        """
        Load data for a single symbol.
        """
        filepath = os.path.join(self.data_dir, f"{symbol}.csv")

        if os.path.exists(filepath):
            return pd.read_csv(filepath, parse_dates=["datetime"])

        if fetch_if_missing:
            print(f"[INFO] Fetching data for {symbol}...")
            df = self._fetch_data_for_symbol(symbol)
            if df is not None:
                df.to_csv(filepath, index=False)
                return df
            else:
                raise ValueError(f"[ERROR] Failed to fetch data for {symbol}")

        raise FileNotFoundError(f"[ERROR] Data for {symbol} not found and fetching disabled.")

    def _fetch_data_for_symbol(self, symbol: str) -> pd.DataFrame:
        """
        Replace this mock implementation with a real data fetch call.
        """
        print(f"[MOCK FETCH] {symbol} from {self.start} to {self.end} at {self.interval}")
        self.quote_client.fetch_historical_bars(
            symbols=self.watchlist,
            start_date=self.start_date,
            end_date=self.end_date, 
            currency=SupportedCurrencies.USD,
            feed = DataFeed.IEX
        )
        # Example mocked structure
        date_range = pd.date_range(start=self.start, end=self.end, freq='D')
        df = pd.DataFrame({
            "datetime": date_range,
            "open": 100 + pd.np.random.randn(len(date_range)),
            "high": 101 + pd.np.random.randn(len(date_range)),
            "low": 99 + pd.np.random.randn(len(date_range)),
            "close": 100 + pd.np.random.randn(len(date_range)),
            "volume": pd.np.random.randint(1000, 5000, size=len(date_range))
        })
        return df
