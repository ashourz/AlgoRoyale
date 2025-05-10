import asyncio
import os
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional
from algo_royale.shared.config.config import load_paths
import pandas as pd
from algo_royale.logging.logger_singleton import LoggerSingleton, LoggerType, Environment
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.backtester.config.config import load_config
from algo_royale.backtester.utils.watchlist import load_watchlist
import dateutil.parser
from alpaca.common.enums import SupportedCurrencies

class BacktestDataLoader:
    def __init__(self):
        try:
            # Load configurations
            self.config = load_config()
            self.paths = load_paths()

            # Validate configurations
            self._validate_config()
            self._validate_paths()

            # Initialize directories and services
            self.data_dir = Path(self.paths["data_ingest_dir"])
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.quote_client = AlpacaQuoteService()
            self.watchlist = load_watchlist(self.paths["watchlist_path"])

            # Parse dates
            self.start_date = dateutil.parser.parse(self.config["start_date"])
            self.end_date = dateutil.parser.parse(self.config["end_date"])

            # Initialize logger
            self.logger = LoggerSingleton(
                LoggerType.BACKTESTING,
                Environment.PRODUCTION
            ).get_logger()

        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize BacktestDataLoader: {e}")

    def _validate_config(self):
        """Ensure required keys are present in the config dictionary."""
        required_keys = ["start_date", "end_date"]
        for key in required_keys:
            if key not in self.config:
                raise KeyError(f"Config is missing required key: '{key}'")

    def _validate_paths(self):
        """Ensure required keys are present in the paths dictionary."""
        required_keys = ["data_ingest_dir", "watchlist_path"]
        for key in required_keys:
            if key not in self.paths:
                raise KeyError(f"Paths is missing required key: '{key}'")
            
    async def load_all(self) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Returns async data generators with automatic data fetching"""
        self.logger.info("Starting async data loading")
        
        # First ensure we have data for all symbols
        await self._ensure_all_data_exists()
        
        # Then prepare the async iterators
        data = {}
        for symbol in self.watchlist:
            try:
                # Use functools.partial to properly bind the symbol
                data[symbol] = lambda s=symbol: self.load_symbol(s)
                self.logger.info(f"Prepared async data loader for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to prepare loader for {symbol}: {str(e)}")
        
        return data

    async def _ensure_all_data_exists(self) -> None:
        """Ensure we have data for all symbols in watchlist"""
        tasks = []
        for symbol in self.watchlist:
            symbol_dir = self.data_dir / symbol
            if not self._has_existing_data(symbol_dir):
                tasks.append(self._fetch_and_save_symbol(symbol))
        
        if tasks:
            self.logger.info(f"Fetching data for {len(tasks)} symbols...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, success in zip(self.watchlist, results):
                if isinstance(success, Exception):
                    self.logger.error(f"Failed to fetch {symbol}: {str(success)}")
                elif not success:
                    self.logger.error(f"Failed to fetch {symbol} (unknown error)")

    def _has_existing_data(self, symbol_dir: Path) -> bool:
        """Check if valid data exists for a symbol"""
        if not symbol_dir.exists():
            return False
        return any(symbol_dir.glob("*.csv"))

    async def load_symbol(self, symbol: str) -> AsyncIterator[pd.DataFrame]:
        """Async generator yielding DataFrames, fetching data if needed"""
        symbol_dir = self.data_dir / symbol
        
        # First ensure we have data
        if not await self._ensure_symbol_data_exists(symbol):
            raise ValueError(f"No data available for {symbol}")
        
        # Then stream the data
        async for df in self._stream_existing_data_async(symbol_dir):
            yield df

    async def _ensure_symbol_data_exists(self, symbol: str) -> bool:
        """Ensure data exists for a specific symbol"""
        symbol_dir = self.data_dir / symbol
        if not self._has_existing_data(symbol_dir):
            self.logger.info(f"No existing data for {symbol}, fetching...")
            return await self._fetch_and_save_symbol(symbol)
        return True

    async def _stream_existing_data_async(self, symbol_dir: Path) -> AsyncIterator[pd.DataFrame]:
        """Async version of streaming existing data"""
        pages = sorted(
            symbol_dir.glob("*.csv"),
            key=lambda x: int(x.stem.split('_')[-1])
        )
        
        self.logger.debug(f"Found {len(pages)} data pages in {symbol_dir}")
        
        for page_path in pages:
            try:
                self.logger.debug(f"Yielding {page_path}")
                # Use to_thread for synchronous file operations
                df = await asyncio.to_thread(
                    pd.read_csv, 
                    page_path, 
                    parse_dates=["timestamp"]
                )
                yield df
            except Exception as e:
                self.logger.error(f"Error reading {page_path}: {str(e)}")
                continue

    async def _fetch_and_save_symbol(self, symbol: str) -> bool:
        """Fetch and save data for a symbol, returning success status"""
        symbol_dir = self.data_dir / symbol
        symbol_dir.mkdir(exist_ok=True)
        
        try:
            page_token = None
            page_count = 0
            total_rows = 0
            
            self.logger.info(f"Fetching data for {symbol} from {self.start_date} to {self.end_date}")
            
            while True:
                page_count += 1
                page_path = symbol_dir / f"{symbol}_page_{page_count}.csv"
                
                # Fetch data from API
                response = await self.quote_client.fetch_historical_bars(
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

                await asyncio.to_thread(
                    df.to_csv,
                    page_path,
                    index=False
                )
                
                self.logger.info(f"Saved page {page_count} for {symbol} with {len(df)} rows")
                
                # Check for more pages
                page_token = response.next_page_token
                if not page_token:
                    break
            
            self.logger.info(f"Finished fetching {symbol}: {page_count} pages, {total_rows} rows")
            return True
            
        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {str(e)}")
            # Clean up partial data
            if page_count == 1 and page_path.exists():
                page_path.unlink()
            return False
        finally:
            await self.quote_client.client.aclose()