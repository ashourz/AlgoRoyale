import glob
from logging import Logger
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from algo_royale.config.config import Config
import pandas as pd
from math import ceil

class BacktestResultsSaver:
    """
    Handles saving backtest results with configurable directory structure.
    Results directory is resolved from configuration file.
    Supports splitting large files by row count.
    """

    def __init__(self, config: Config, logger: Logger, max_rows_per_file: int = 1_000_000):
        """
        Initialize the results saver with directory from config.
        """
        backtester_dir_string = config.get("paths.backtester", "backtest_dir")
        if not backtester_dir_string:
            raise ValueError("Backtester directory not specified in config")
        self.backtest_dir = Path(backtester_dir_string)
        self.backtest_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        self.max_rows_per_file = max_rows_per_file
        self.logger.info(f"Results will be saved to: {self.backtest_dir}")

    def has_existing_results(self, strategy_name: str, symbol: str) -> bool:
        """
        Check if results exist for this strategy-symbol pair in current run directory only.
        """
        search_dir = self.backtest_dir / strategy_name / symbol
        pattern = str(search_dir / f"{strategy_name}_{symbol}_*.csv")
        return len(glob.glob(pattern)) > 0

    def save_strategy_results(
        self,
        strategy_name: str,
        symbol: str,
        results_df: pd.DataFrame,
        timestamp: Optional[datetime] = None
    ) -> list[str]:
        """
        Save backtest results for a single strategy-symbol pair. Splits into multiple files if needed.
        Returns a list of file paths.
        """
        if results_df is None:
            raise ValueError("None DataFrame provided")
        if not isinstance(results_df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(results_df)}")
        
        timestamp = timestamp or datetime.now()
        output_dir = self.backtest_dir / strategy_name / symbol
        output_dir.mkdir(parents=True, exist_ok=True)

        if 'strategy' not in results_df.columns:
            results_df = results_df.assign(strategy=strategy_name)
        if 'symbol' not in results_df.columns:
            results_df = results_df.assign(symbol=symbol)

        total_rows = len(results_df)
        num_parts = ceil(total_rows / self.max_rows_per_file)
        filepaths = []

        for part_idx in range(num_parts):
            chunk_df = results_df.iloc[
                part_idx * self.max_rows_per_file : (part_idx + 1) * self.max_rows_per_file
            ]
            part_suffix = f"_part{part_idx+1}" if num_parts > 1 else ""
            filename = f"{strategy_name}_{symbol}_{timestamp.strftime('%H%M%S')}{part_suffix}.csv"
            filepath = output_dir / filename

            try:
                chunk_df.to_csv(filepath, index=False)
                self.logger.info(f"Saved part {part_idx+1}/{num_parts} to {filepath}")
                filepaths.append(str(filepath))
            except Exception as e:
                self.logger.error(f"Failed to save chunk {part_idx+1} for {strategy_name}/{symbol}: {e}")
                raise

        return filepaths

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
        output_dir = self.backtest_dir / report_name
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename

        try:
            combined_dfs = []
            for symbol, strategy_results in all_results.items():
                for strategy_name, df in strategy_results.items():
                    if df is not None:
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
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Failed to save aggregated report: {e}")
            raise
