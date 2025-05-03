import glob
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType
from algo_royale.trade_another_day.config.config import load_config

class BackTesterResultsSaver:
    """
    Handles saving backtest results with configurable directory structure.
    Results directory is resolved from configuration file.
    """
    
    def __init__(self):
        """
        Initialize the results saver with directory from config.
        
        Args:
            config_path: Optional path to config file. If None, uses default config.
        """
        self.config = load_config()
        self.results_dir = self.config["results_dir"]
        os.makedirs(self.results_dir, exist_ok=True)
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        
        self.logger.info(f"Results will be saved to: {self.results_dir}")

    def has_existing_results(self, strategy_name: str, symbol: str) -> bool:
        """
        Check if results exist for this strategy-symbol pair in current run directory only.
        Maintains your existing directory structure without checking historical folders.
        """
        # Match files with pattern: {strategy}_{symbol}_*.csv in current run directory
        pattern = os.path.join(self.results_dir, f"{strategy_name}_{symbol}_*.csv")
        return len(glob.glob(pattern)) > 0
    
    def save_strategy_results(
        self,
        strategy_name: str,
        symbol: str,
        results_df: pd.DataFrame,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Save backtest results for a single strategy-symbol pair.
        
        Args:
            strategy_name: Name of the strategy
            symbol: Ticker symbol
            results_df: DataFrame containing results
            timestamp: Optional timestamp for filename
            
        Returns:
            Path to the saved file
        """
        timestamp = timestamp or datetime.now()
        filename = f"{strategy_name}_{symbol}_{timestamp.strftime('%H%M%S')}.csv"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            # Ensure required columns exist
            if 'strategy' not in results_df.columns:
                results_df = results_df.assign(strategy=strategy_name)
                
            if 'symbol' not in results_df.columns:
                results_df = results_df.assign(symbol=symbol)
                
            results_df.to_csv(filepath, index=False)
            self.logger.info(f"Saved results to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save results for {strategy_name}/{symbol}: {e}")
            raise

    def save_aggregated_report(
        self,
        all_results: Dict[str, Dict[str, pd.DataFrame]],
        report_name: str = "aggregated_report"
    ) -> str:
        """
        Save combined results from multiple strategies and symbols.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_name}_{timestamp}.csv"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            combined_dfs = []
            for symbol, strategy_results in all_results.items():
                for strategy_name, df in strategy_results.items():
                    if df is not None:
                        # Ensure strategy and symbol columns exist
                        df = df.copy()
                        if 'strategy' not in df.columns:
                            df['strategy'] = strategy_name
                        if 'symbol' not in df.columns:
                            df['symbol'] = symbol
                        combined_dfs.append(df)
            
            if not combined_dfs:
                self.logger.warning("No results to aggregate")
                return ""
                
            combined_df = pd.concat(combined_dfs, ignore_index=True)
            combined_df.to_csv(filepath, index=False)
            self.logger.info(f"Saved aggregated report to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save aggregated report: {e}")
            raise