import os
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType
from algo_royale.shared.models.alpaca_market_data.enums import DataFeed
from algo_royale.shared.service.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.trade_another_day.config.config import load_config
from algo_royale.trade_another_day.utils.watchlist import load_watchlist
import pandas as pd
from typing import Dict, Iterator
import dateutil.parser
from alpaca.common.enums import SupportedCurrencies

class BacktestDataLoader:
    def __init__(self):
        self.config = load_config()
        self.data_dir = self.config["data_dir"]
        os.makedirs(self.data_dir, exist_ok=True)
        self.quote_client = AlpacaQuoteService()
        self.watchlist = load_watchlist(self.config["watchlist_path"])
        
        # Validate and parse dates
        self.start_date = dateutil.parser.parse(self.config["start_date"])
        self.end_date = dateutil.parser.parse(self.config["end_date"])
        
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self._loaded_symbols = set()

    def load_all(self) -> Dict[str, Iterator[pd.DataFrame]]:
        """Load data for all symbols, optionally forcing fresh fetch"""
        self.logger.info(f"Starting data loading")
        data = {}
        for symbol in self.watchlist:
            try:
                if symbol not in self._loaded_symbols:
                    self.logger.info(f"Processing {symbol}")
                    data[symbol] = self.load_symbol(symbol)
                    self._loaded_symbols.add(symbol)
                    self.logger.info(f"Successfully loaded data for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to load {symbol}: {str(e)}")
                continue
        return data

    def load_symbol(self, symbol: str) -> Iterator[pd.DataFrame]:
        """Load data for a single symbol with force_fetch option"""
        symbol_dir = os.path.join(self.data_dir, symbol)
        self.logger.debug(f"Symbol directory for {symbol}: {symbol_dir}")

        # Check for existing data
        if os.path.exists(symbol_dir):
            num_pages = len([f for f in os.listdir(symbol_dir) if f.endswith('.csv')])
            if num_pages > 0:
                self.logger.info(f"Found {num_pages} existing data pages for {symbol}")
                return self._stream_existing_data(symbol_dir)
        
        # Fetch if no existing data
        self.logger.info(f"No existing data found for {symbol}, fetching...")
        if not self._fetch_and_save_symbol(symbol):
            raise ValueError(f"Failed to fetch data for {symbol}")
        return self._stream_existing_data(symbol_dir)

    def _fetch_and_save_symbol(self, symbol: str) -> bool:
        """Fetch and save data for a symbol, returning success status"""
        symbol_dir = os.path.join(self.data_dir, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        
        try:
            page_token = None
            page_count = 0
            total_rows = 0
            self.logger.info(f"Initiating data fetch for {symbol} from {self.start_date} to {self.end_date}")            
            while True:
                page_count += 1
                page_path = os.path.join(symbol_dir, f"{symbol}_page_{page_count}.csv")
                
                # Fetch data from API
                response = self.quote_client.fetch_historical_bars(
                    symbols=[symbol],
                    start_date=self.start_date,
                    end_date=self.end_date,
                    currency=SupportedCurrencies.USD,
                    feed=DataFeed.IEX,
                    page_token=page_token
                )
                
                # Check response
                if not response or not response.symbol_bars.get(symbol):
                    if page_count == 1:
                        self.logger.warning(f"No data returned for {symbol}")
                        return False
                    break
                
                # Process and save page
                bars = response.symbol_bars[symbol]
                df = pd.DataFrame([bar.model_dump() for bar in bars])
                df["symbol"] = symbol
                total_rows += len(df)

                with open(page_path, 'w') as f:
                    df.to_csv(f, index=False)
                
                self.logger.info(f"Saved page {page_count} for {symbol} with {len(df)} rows")
                
                # Check for more pages
                page_token = response.next_page_token
                if not page_token:
                    break
            
            self.logger.info(f"Finished fetching {page_count} pages with {total_rows} total rows for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {str(e)}: {e}")
            return False

    def _stream_existing_data(self, symbol_dir: str) -> Iterator[pd.DataFrame]:
        """Stream existing data pages with proper error handling"""
        try:
            # Get sorted list of page files
            pages = sorted(
                [f for f in os.listdir(symbol_dir) if f.endswith('.csv')],
                key=lambda x: int(x.split('_')[-1].split('.')[0])
            )
            
            self.logger.debug(f"Found {len(pages)} data pages in {symbol_dir}")

            for i, page in enumerate(pages, 1):
                page_path = os.path.join(symbol_dir, page)
                try:
                    self.logger.info(f"Streaming {page}")
                    with open(page_path, 'r') as f:
                        df = pd.read_csv(f, parse_dates=["timestamp"])
                        self.logger.debug(f"Yielding page {i}/{len(pages)} with {len(df)} rows")
                        yield df
                except Exception as e:
                    self.logger.error(f"Error reading {page}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error streaming data: {str(e)}")
            raise