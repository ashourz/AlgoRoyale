from glob import glob
import os
from algo_royale.shared.models.alpaca_market_data.alpaca_bar import Bar
from algo_royale.trade_another_day.utils.results_saver import BackTesterResultsSaver
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestEngine:
    def __init__(self, strategies: List[Strategy]):
        """
        Initialize the backtest engine with strategy-aware results.
        
        Args:
            strategies: List of strategy objects to test
        """
        self.strategies = strategies
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self.results_saver = BackTesterResultsSaver()
        self._processed_pairs = set()

    def run_backtest(self, data: Dict[str, pd.DataFrame]) -> None:
        """Run backtest using DataFrames directly"""
        self.logger.info("Starting DataFrame-based backtest...")
        
        for symbol, df in data.items():
            for strategy in self.strategies:
                strategy_name = strategy.__class__.__name__
                pair_key = f"{symbol}_{strategy_name}"
                
                if self._should_skip_pair(pair_key, strategy_name, symbol):
                    continue
                
                try:
                    self.logger.info(f"Processing {symbol} with {strategy_name}...")
                    
                    # Pass DataFrame directly to strategy
                    signals = strategy.generate_signals(df.copy())
                    
                    # Create results (add strategy column)
                    results_df = df.copy()
                    results_df['signal'] = signals
                    results_df['strategy'] = strategy_name
                    
                    # Save results
                    self.results_saver.save_strategy_results(
                        strategy_name=strategy_name,
                        symbol=symbol,
                        results_df=results_df
                    )
                    
                    self._processed_pairs.add(pair_key)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {symbol}-{strategy_name}: {e}")
    
    def _should_skip_pair(self, pair_key: str, strategy_name: str, symbol: str) -> bool:
        """Determine if we should skip processing this symbol-strategy pair."""
        if pair_key in self._processed_pairs:
            self.logger.info(f"Skipping already processed pair: {symbol}-{strategy_name}")
            return True
            
        if self.results_saver.has_existing_results(strategy_name, symbol):
            self.logger.info(f"Found existing results for {symbol}-{strategy_name}, skipping...")
            self._processed_pairs.add(pair_key)
            return True
            
        return False

    def _process_pair(self, strategy: Strategy, symbol: str, bars: List[Bar]) -> None:
        """Process and save results for a single symbol-strategy pair."""
        strategy_name = strategy.__class__.__name__
        pair_key = f"{symbol}_{strategy_name}"
        
        try:
            self.logger.info(f"Processing {symbol} with {strategy_name}...")
            
            # Generate signals
            signals = strategy.generate_signals(bars)
            
            # Create results with strategy column
            results_df = self._create_results_df(bars, signals, strategy_name)
            
            # Save results
            self.results_saver.save_strategy_results(
                strategy_name=strategy_name,
                symbol=symbol,
                results_df=results_df
            )
            
            self._processed_pairs.add(pair_key)
            
        except Exception as e:
            self.logger.error(f"Failed to process {symbol}-{strategy_name}: {e}")

    def _create_results_df(self, bars: List[Bar], signals: List[str], strategy_name: str) -> pd.DataFrame:
        """
        Create results DataFrame with strategy column included.
        """
        return pd.DataFrame({
            'timestamp': [bar.timestamp for bar in bars],
            'open': [bar.open_price for bar in bars],
            'high': [bar.high_price for bar in bars],
            'low': [bar.low_price for bar in bars],
            'close': [bar.close_price for bar in bars],
            'volume': [bar.volume for bar in bars],
            'signal': signals,
            'strategy': strategy_name  # Include strategy name in results
        })