from typing import Callable, Dict, List, Iterator
import pandas as pd
from algo_royale.trade_another_day.utils.results_saver import BackTesterResultsSaver
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestEngine:
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self.results_saver = BackTesterResultsSaver()
        self._processed_pairs = set()

    def run_backtest(self, data: Dict[str, Callable[[], Iterator[pd.DataFrame]]]) -> None:
        self.logger.info("Starting streaming backtest...")
        
        for symbol, df_iterator_factory in data.items():
            for strategy in self.strategies:
                df_iterator = df_iterator_factory()
                strategy_name = strategy.__class__.__name__
                pair_key = f"{symbol}_{strategy_name}"
                
                if self._should_skip_pair(pair_key, strategy_name, symbol):
                    continue
                
                try:
                    self.logger.info(f"Processing {symbol} with {strategy_name}...")
                    all_results = []
                    page_count = 0
                    processed_rows = 0
                    
                    for page_df in df_iterator:
                        page_count += 1
                        try:
                            # Skip empty pages
                            if page_df.empty:
                                self.logger.debug(f"Empty page {page_count} for {symbol}")
                                continue
                            
                            # Validate data quality
                            try:
                                self._validate_data_quality(page_df)
                            except ValueError as ve:
                                self.logger.warning(
                                    f"Data quality issue in page {page_count} for {symbol}: {str(ve)}"
                                )
                                continue
                            
                            # Generate signals
                            signals = strategy.generate_signals(page_df.copy())
                            
                            # Validate strategy output
                            try:
                                self._validate_strategy_output(strategy, page_df, signals)
                            except ValueError as ve:
                                self.logger.warning(
                                    f"Strategy validation failed for {symbol} page {page_count}: {str(ve)}"
                                )
                                continue
                                
                            # Prepare results
                            result_df = page_df.copy()
                            result_df['signal'] = signals
                            result_df['strategy'] = strategy_name
                            result_df['symbol'] = symbol
                            
                            all_results.append(result_df)
                            processed_rows += len(result_df)
                            
                        except Exception as e:
                            self.logger.error(
                                f"Error processing page {page_count} for {symbol}-{strategy_name}: {e}"
                            )
                            continue
                    
                    self.logger.info(
                        f"{symbol}-{strategy_name} processed {len(all_results)} pages "
                        f"({processed_rows} total rows)"
                    )
                    
                    if not all_results:
                        self.logger.warning(f"No valid data processed for {symbol}-{strategy_name}")
                        continue
                    
                    combined_results = pd.concat(all_results, ignore_index=True)
                    self.results_saver.save_strategy_results(
                        strategy_name=strategy_name,
                        symbol=symbol,
                        results_df=combined_results
                    )
                    
                    self._processed_pairs.add(pair_key)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {symbol}-{strategy_name}: {e}")
                    
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
        """Check for common data issues that might affect strategy processing"""
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
        """Validate strategy output matches input dimensions and types"""
        if len(signals) != len(df):
            raise ValueError(
                f"Strategy {strategy.__class__.__name__} returned "
                f"{len(signals)} signals for {len(df)} rows"
            )
            
        if not isinstance(signals, pd.Series):
            raise ValueError("Strategy must return pandas Series")
            
        if signals.isnull().any():
            raise ValueError("Strategy returned signals containing null values")
