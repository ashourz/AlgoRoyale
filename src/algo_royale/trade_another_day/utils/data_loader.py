from datetime import datetime
import os
from algo_royale.trade_another_day.utils.validation_utils import validate_date
import dateutil
import pandas as pd
from algo_royale.shared.models.alpaca_market_data.enums import DataFeed
from algo_royale.shared.service.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.trade_another_day.config.config import load_config
from algo_royale.trade_another_day.utils.watchlist import load_watchlist
from alpaca.common.enums import SupportedCurrencies

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestDataLoader:
    def __init__(self):
        self.config = load_config()
        self.data_dir = self.config["data_dir"]
        os.makedirs(self.data_dir, exist_ok=True)
        self.quote_client = AlpacaQuoteService()
        self.watchlist = load_watchlist(self.config["watchlist_path"])
        
        # Validate dates
        self.raw_start_date = self.config["start_date"]
        self.raw_end_date = self.config["end_date"]
        validate_date(self.raw_start_date, "start_date")
        validate_date(self.raw_end_date, "end_date")
        
        # Parse dates
        self.start_date = dateutil.parser.parse(self.raw_start_date)
        self.end_date = dateutil.parser.parse(self.raw_end_date)
        
        self.interval = self.config["interval"]
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self._loaded_symbols = set()  # Track which symbols we've already loaded

    def load_all(self, fetch_if_missing=True) -> dict:
        """
        Loads data for all symbols in the watchlist.
        Returns a dict of {symbol: DataFrame}
        """
        data = {}
        for symbol in self.watchlist:
            try:
                if symbol not in self._loaded_symbols:
                    data[symbol] = self.load_symbol(symbol, fetch_if_missing)
                    self._loaded_symbols.add(symbol)
            except Exception as e:
                self.logger.warning(f"Could not load data for {symbol}: {e}")
        return data

    def load_symbol(self, symbol: str, fetch_if_missing=True) -> pd.DataFrame:
        """
        Load data for a single symbol.
        Returns cached data if already loaded, otherwise loads from disk or API.
        """
        filepath = os.path.join(self.data_dir, f"{symbol}.csv")

        # Check if we already have this data in memory
        if symbol in self._loaded_symbols:
            self.logger.debug(f"Using cached data for {symbol}")
            return pd.read_csv(filepath, parse_dates=["timestamp"])

        # Check if data exists on disk
        if os.path.exists(filepath):
            self.logger.info(f"Loading existing data for {symbol} from {filepath}")
            return pd.read_csv(filepath, parse_dates=["timestamp"])

        # Fetch from API if allowed
        if fetch_if_missing:
            self.logger.info(f"Fetching data for {symbol}...")
            df = self._fetch_data_for_symbol(symbol)
            if df is not None:
                df.to_csv(filepath, index=False)
                self._loaded_symbols.add(symbol)
                return df
            else:
                raise ValueError(f"Failed to fetch data for {symbol}")

        raise FileNotFoundError(f"Data for {symbol} not found and fetching disabled")
    
    def _fetch_data_for_symbol(self, symbol: str) -> pd.DataFrame:
        """Fetch data from Alpaca API for a single symbol"""
        try:
            bars_response = self.quote_client.fetch_historical_bars(
                symbols=[symbol],
                start_date=self.start_date,
                end_date=self.end_date,
                currency=SupportedCurrencies.USD,
                feed=DataFeed.IEX
            )

            bars = bars_response.symbol_bars.get(symbol, [])
            if not bars:
                self.logger.warning(f"No bars returned for {symbol}")
                return None

            # Convert to DataFrame
            rows = [bar.model_dump() for bar in bars]
            df = pd.DataFrame(rows)
            df["symbol"] = symbol
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None