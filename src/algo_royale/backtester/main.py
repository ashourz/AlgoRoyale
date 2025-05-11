from logging import Logger
from typing import Callable, Dict, List, AsyncIterator
from algo_royale.models.alpaca_market_data.alpaca_bar import Bar
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.backtester.core.engine import BacktestEngine
from algo_royale.backtester.utils.data_loader import BacktestDataLoader
from algo_royale.strategies.moving_average_strategy import MovingAverageStrategy
import pandas as pd
import asyncio

from functools import partial
from typing import Callable, Dict, List, AsyncIterator
import pandas as pd
import asyncio

class BacktestRunner:
    def __init__(self, data_loader: BacktestDataLoader, engine: BacktestEngine, logger: Logger):
        self.logger = logger
        self.config = self._validate_config({})
        self.strategies = self._initialize_strategies()
        self.data_loader = data_loader
        self.engine = engine

    def _validate_config(self, config: dict) -> dict:
        """Validate and normalize configuration"""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        # Set default column mappings
        config.setdefault('data_columns', {
            'open_price': 'open',
            'high_price': 'high',
            'low_price': 'low',
            'close_price': 'close'
        })
        
        return config
    
    def _initialize_strategies(self) -> List[Strategy]:
        """Initialize and return the list of strategies to test."""
        return [
            MovingAverageStrategy(short_window=50, long_window=200),
            # Add more strategies as needed
        ]
        
    async def _load_and_prepare_data(self) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Safe data loading with proper resource handling"""
        self.logger.info("Loading market data...")
        
        try:
            raw_data = await self.data_loader.load_all()
            if not raw_data:
                raise ValueError("Data loader returned empty result")
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return {}

        prepared_data = {}
        
        for symbol, async_iterator_factory in raw_data.items():
            try:
                # Create properly bound preparer
                preparer = self._create_data_preparer(symbol, async_iterator_factory)
                prepared_data[symbol] = preparer
                self.logger.info(f"Prepared data iterator for {symbol}")
                
            except Exception as e:
                self.logger.error(f"Failed preparing {symbol} data: {e}")
                continue
                
        return prepared_data

    def _create_data_preparer(self, symbol: str, iterator_factory):
        """Factory for properly bound data preparers"""
        async def preparer():
            iterator = iterator_factory()
            try:
                async for df in iterator:
                    try:
                        df = self._normalize_dataframe(df, symbol)
                        yield df
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol} data: {e}")
                        continue
            finally:
                if hasattr(iterator, 'aclose'):
                    await iterator.aclose()
                    
        return preparer

    def _normalize_dataframe(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Ensure consistent dataframe structure"""
        # Validate input
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Expected DataFrame for {symbol}, got {type(df)}")
            
        if df.empty:
            self.logger.debug(f"Empty dataframe for {symbol}")
            return df
            
        # Rename columns according to config
        df = df.rename(columns=self.config['data_columns'])
        
        # Validate required columns
        required = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in {symbol} data: {missing}")
            
        return df

    async def _validate_iterator(self, symbol, iterator):
        if iterator is None:
            raise ValueError(f"Null iterator for {symbol}")
        return iterator
    
    async def run_async(self):
        """Pure async entry point"""
        try:
            data = await self._load_and_prepare_data()
            if not data:
                self.logger.error("No valid data available")
                return False
            
            await self.engine.run_backtest(
                strategies=self.strategies, 
                data=data)
            self.logger.info("Backtest completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    def run(self):
        """Synchronous wrapper"""
        return asyncio.run(self.run_async())

async def async_cli(runner: BacktestRunner):
    """Async command line interface entry point"""
    success = await runner.run_async()
    exit(0 if success else 1)

def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.container import di_container  # Import here to avoid circular dependency
    runner = di_container.backtest_runner()
    asyncio.run(async_cli(runner))

if __name__ == "__main__":
    cli()