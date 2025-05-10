import asyncio
from pathlib import Path
from typing import Callable, Dict, List, AsyncIterator, Union
import pandas as pd
from algo_royale.backtester.utils.results_saver import BackTesterResultsSaver
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestEngine:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self.results_saver = BackTesterResultsSaver()
        self._processed_pairs = set()

    async def run_backtest(self, data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]) -> None:
        """Pure async implementation for processing streaming data"""
        if not data:
            self.logger.error("No data available - check your data paths and files")
            return
            
        # Verify at least some files exist
        for symbol in data.keys():
            data_path = Path(f"data/backtesting/bars/{symbol}")
            if not data_path.exists():
                self.logger.error(f"Data path does not exist: {data_path}")
            elif not any(data_path.glob("*.csv")):
                self.logger.error(f"No CSV files found in {data_path}")
        
        try:
            self.logger.info("Starting async backtest...")
            
            for symbol, async_iterator_factory in data.items():
                for strategy in self.strategies:
                    strategy_name = strategy.__class__.__name__
                    pair_key = f"{symbol}_{strategy_name}"
                    
                    if self._should_skip_pair(pair_key, strategy_name, symbol):
                        continue
                    
                    try:
                        self.logger.info(f"Processing {symbol} with {strategy_name} (expecting data from {symbol})")
                        all_results = []
                        page_count = 0
                        processed_rows = 0
                        
                        # Get the async iterator
                        async_df_iterator = async_iterator_factory()
                        
                        async for page_df in async_df_iterator:
                            page_count += 1
                            try:
                                result_df = await self._process_single_page(
                                    symbol, 
                                    strategy, 
                                    page_df, 
                                    page_count
                                )
                                if result_df is not None:
                                    all_results.append(result_df)
                                    processed_rows += len(result_df)
                                    
                            except Exception as e:
                                self.logger.error(
                                    f"Error processing page {page_count} for {symbol}-{strategy_name}: {str(e)}"
                                )
                                continue
                        
                        await self._save_and_finalize(
                            symbol,
                            strategy_name,
                            all_results,
                            processed_rows
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Failed to process {symbol}-{strategy_name}: {str(e)}")
        except asyncio.CancelledError:
            self.logger.warning("Backtest cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Critical backtest failure: {e}")
            raise

    async def _process_single_page(
        self,
        symbol: str,
        strategy: Strategy,
        page_df: pd.DataFrame,
        page_num: int
    ) -> Union[pd.DataFrame, None]:
        """Process a single page of data with proper signal handling"""
        if page_df.empty:
            self.logger.debug(f"Empty page {page_num} for {symbol}")
            return None
        
        try:
            # Validate input data
            self._validate_data_quality(page_df)
            
            # Generate and validate signals
            signals = strategy.generate_signals(page_df.copy())
            self.logger.debug(f"Generated signals: {type(signals)} with length {len(signals)}")
            self._validate_strategy_output(strategy, page_df, signals)
            
            # Create result DataFrame
            result_df = page_df.copy()
            result_df['signal'] = signals.values  # Important: use .values
            result_df['strategy'] = strategy.__class__.__name__
            result_df['symbol'] = symbol
            
            return result_df
            
        except Exception as e:
            self.logger.error(
                f"Critical error processing page {page_num} for {symbol}-{strategy.__class__.__name__}: {str(e)}"
            )
            raise
                
    async def _save_and_finalize(   
        self,
        symbol: str,
        strategy_name: str,
        all_results: List[pd.DataFrame],
        processed_rows: int
    ) -> None:
        """Save results and log final output"""
        self.logger.info(
            f"{symbol}-{strategy_name} processed {len(all_results)} pages "
            f"({processed_rows} total rows)"
        )
        
        if not all_results:
            self.logger.warning(f"No valid data processed for {symbol}-{strategy_name}")
            return
        
        combined_results = pd.concat(all_results, ignore_index=True)
        await asyncio.to_thread(
            self.results_saver.save_strategy_results,
            strategy_name=strategy_name,
            symbol=symbol,
            results_df=combined_results
        )
        
        self._processed_pairs.add(f"{symbol}_{strategy_name}")

    def _should_skip_pair(self, pair_key: str, strategy_name: str, symbol: str) -> bool:
        if pair_key in self._processed_pairs:
            self.logger.info(f"Skipping already processed pair: {symbol}-{strategy_name}")
            return True

        if self.results_saver.has_existing_results(strategy_name, symbol):
            self.logger.info(f"Found existing results for {symbol}-{strategy_name}, skipping...")
            self._processed_pairs.add(pair_key)
            return True

        return False
    
    def _validate_data_quality(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Empty DataFrame received")
            
        if df.isnull().any().any():
            missing = df.columns[df.isnull().any()].tolist()
            raise ValueError(f"Data contains null values in columns: {missing}")
            
        if (df['close'] <= 0).any():
            raise ValueError("Invalid close prices (<= 0) detected")
            
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            raise ValueError("Timestamp column must be datetime type")

    def _validate_strategy_output(self, strategy: Strategy, df: pd.DataFrame, signals: pd.Series) -> None:
        if len(signals) != len(df):
            raise ValueError(
                f"Strategy {strategy.__class__.__name__} returned "
                f"{len(signals)} signals for {len(df)} rows"
            )
            
        if not isinstance(signals, pd.Series):
            raise ValueError("Strategy must return pandas Series")
            
        if signals.isnull().any():
            raise ValueError("Strategy returned signals containing null values")