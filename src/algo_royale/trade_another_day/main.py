from typing import Callable, Dict, List, Iterator, Tuple
from algo_royale.shared.models.alpaca_market_data.alpaca_bar import Bar
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.trade_another_day.core.engine import BacktestEngine
from algo_royale.trade_another_day.config.config import load_config
from algo_royale.trade_another_day.utils.data_loader import BacktestDataLoader
from algo_royale.shared.strategies.moving_average_strategy import MovingAverageStrategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType
import pandas as pd

class BacktestRunner:
    def __init__(self):
        """
        Initialize the backtest runner with logging and configuration.
        """
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self.config = load_config()
        self.strategies = self._initialize_strategies()
        self.data_loader = BacktestDataLoader()
        self.engine = None

    def _initialize_strategies(self) -> List[Strategy]:
        """Initialize and return the list of strategies to test."""
        return [
            MovingAverageStrategy(short_window=50, long_window=200),
            # Add more strategies as needed
        ]
        
    def _load_and_prepare_data(self) -> Dict[str, Callable[[], Iterator[pd.DataFrame]]]:
        self.logger.info("Loading market data...")
        raw_data = self.data_loader.load_all()
        
        prepared_data = {}
        for symbol, df_iterator in raw_data.items():
            try:
                # Create a proper generator class to avoid closure issues
                class PagePreparer:
                    def __init__(self, iterator, symbol, logger):
                        self.iterator = iterator
                        self.symbol = symbol
                        self.logger = logger
                    
                    def __iter__(self):
                        for df in self.iterator:
                            try:
                                df = df.rename(columns={
                                    'open_price': 'open',
                                    'high_price': 'high',
                                    'low_price': 'low',
                                    'close_price': 'close'
                                })
                                
                                required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                                if not all(col in df.columns for col in required_columns):
                                    missing = [col for col in required_columns if col not in df.columns]
                                    self.logger.error(f"Missing columns in {self.symbol} data: {missing}")
                                    continue
                                
                                yield df
                                
                            except Exception as e:
                                self.logger.error(f"Failed to prepare {self.symbol} page: {str(e)}")
                                continue
                
                # Create a factory function that properly instantiates the preparer
                def create_preparer(sym, it):
                    return iter(PagePreparer(it, sym, self.logger))
                    
                prepared_data[symbol] = lambda s=symbol, i=df_iterator: create_preparer(s, i)
                self.logger.info(f"Prepared data iterator for {symbol}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize data preparation for {symbol}: {str(e)}")
                continue
                
        return prepared_data

    def run(self):
        """Execute the complete backtest workflow."""
        try:
            self.engine = BacktestEngine(
                strategies=self.strategies
            )

            # Load and prepare data
            data = self._load_and_prepare_data()
            if not data:
                self.logger.error("No valid data available for backtesting")
                return False

            # Run backtest
            self.logger.info("Starting backtest...")
            self.engine.run_backtest(data)
            
            self.logger.info("Backtest completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}", exc_info=True)
            return False

def cli():
    """Command line interface entry point."""
    runner = BacktestRunner()
    success = runner.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    cli()