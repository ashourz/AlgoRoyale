import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyColumns,
    SignalStrategyExecutorColumns,
)
from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.maps.strategy_class_map import SYMBOL_STRATEGY_CLASS_MAP
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy_factory.signal.strategy_factory import (
    StrategyFactory,
)
from algo_royale.logging.loggable import Loggable


class PortfolioMatrixLoader:
    def __init__(
        self,
        strategy_backtest_executor: StrategyBacktestExecutor,
        asset_matrix_preparer: AssetMatrixPreparer,
        stage_data_manager: StageDataManager,
        stage_data_loader: StageDataLoader,
        strategy_factory: StrategyFactory,
        data_dir: str,
        optimization_root: str,
        signal_summary_json_filename: str,
        symbol_signals_filename: str,
        logger: Loggable,
    ):
        self.asset_matrix_preparer = asset_matrix_preparer
        self.stage_data_manager = stage_data_manager
        self.stage_data_loader = stage_data_loader
        self.strategy_factory = strategy_factory
        self.data_dir = data_dir
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.signal_summary_json_filename = signal_summary_json_filename
        self.symbol_signals_filename = symbol_signals_filename
        self.executor = strategy_backtest_executor
        self.logger = logger
        self.stage = BacktestStage.PORTFOLIO_MATRIX_LOADER

    async def get_portfolio_matrix(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Oversees the workflow: runs backtest and save signals, then compiles and returns the asset-matrix DataFrame."""
        await self._run_backtest_and_save_signals(symbols, start_date, end_date)
        return await self._compile_portfolio_matrix(
            symbols,
            start_date,
            end_date,
            symbol_col=SignalStrategyColumns.SYMBOL,
            timestamp_col=SignalStrategyColumns.TIMESTAMP,
        )

    async def _run_backtest_and_save_signals(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
    ):
        """
        Runs backtest for each symbol in the watchlist with the specified strategy,
        checking if the backtest has already been run for the current stage.
        For each symbol, if the backtest has not been run, it will run the backtest and save the results."""
        import asyncio

        try:
            self.logger.info(
                f"[PortfolioMatrixLoader] Running backtest for symbols: {symbols} | {start_date} to {end_date}"
            )
            tasks = []
            for symbol in symbols:

                async def process_symbol(symbol=symbol):
                    try:
                        self.logger.info(
                            f"[PortfolioMatrixLoader] Checking backtest file for {symbol} | {start_date} to {end_date}"
                        )
                        if not self._has_backtest_run(
                            symbol=symbol, start_date=start_date, end_date=end_date
                        ):
                            self.logger.info(
                                f"[PortfolioMatrixLoader] No optimized strategy signals for {symbol}, running backtest..."
                            )
                            strategy_instance = self._get_optimized_strategy(symbol)
                            if not strategy_instance:
                                self.logger.warning(
                                    f"[PortfolioMatrixLoader] No viable strategy found for {symbol}, skipping backtest."
                                )
                                return
                            await self._run_and_save_symbol_data(
                                symbol, strategy_instance, start_date, end_date
                            )
                        else:
                            self.logger.info(
                                f"[PortfolioMatrixLoader] Optimized strategy signals already exist for {symbol}, skipping backtest."
                            )
                    except Exception as e:
                        self.logger.error(
                            f"[PortfolioMatrixLoader] Error running backtest for {symbol}: {e}"
                        )

                tasks.append(process_symbol())
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(
                f"[PortfolioMatrixLoader] Failed to run backtest for symbols: {symbols} | {e}"
            )

    def _has_backtest_run(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if backtest has already been run for the current stage, for the specific symbol and date range."""
        try:
            return self.stage_data_manager.is_symbol_stage_done(
                stage=self.stage,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            self.logger.error(
                f"Error checking portfolio symbol backtest results for {symbol} in start_date: {start_date}, end_date: {end_date}: {e}"
            )
            return False

    async def _compile_portfolio_matrix(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        symbol_col: str = SignalStrategyColumns.SYMBOL,
        timestamp_col: str = SignalStrategyColumns.TIMESTAMP,
    ) -> Optional[pd.DataFrame]:
        """
        Compiles the portfolio matrix from individual symbol data asynchronously.

        Args:
            symbols (List[str]): List of symbols to include.
            start_date (datetime): Start date for data window.
            end_date (datetime): End date for data window.
            symbol_col (str): Column name for symbol.
            timestamp_col (str): Column name for timestamp.

        Returns:
            Optional[pd.DataFrame]: Compiled portfolio matrix, or None if error.

        Note:
            For large symbol lists, this step is parallelized using asyncio for I/O bound operations.
        """
        import asyncio

        try:

            async def load_symbol(symbol):
                self.logger.info(
                    f"[PortfolioMatrixLoader] Loading data for {symbol} from {start_date} to {end_date}"
                )
                loop = asyncio.get_running_loop()
                # Run the blocking _load_symbol_data in a thread
                df = await loop.run_in_executor(
                    None,
                    self._load_symbol_data,
                    symbol,
                    start_date,
                    end_date,
                )
                if df is None:
                    self.logger.warning(
                        f"[PortfolioMatrixLoader] No data found for {symbol} in range {start_date} to {end_date}, skipping."
                    )
                    return None
                if symbol_col not in df.columns:
                    df[symbol_col] = symbol
                return df

            tasks = [load_symbol(symbol) for symbol in symbols]
            dfs = [df for df in await asyncio.gather(*tasks) if df is not None]
            if not dfs:
                self.logger.error(
                    "[PortfolioMatrixLoader] No valid dataframes to concatenate for portfolio matrix."
                )
                return None
            self.logger.info(
                f"[PortfolioMatrixLoader] Compiling portfolio matrix for {len(dfs)} symbols."
            )
            all_df = pd.concat(dfs, axis=0, ignore_index=True)
            matrix = self.asset_matrix_preparer.prepare(
                all_df,
                symbol_col=symbol_col,
                timestamp_col=timestamp_col,
            )
            return matrix
        except Exception as e:
            self.logger.error(
                f"[PortfolioMatrixLoader] Error compiling portfolio matrix: {e}"
            )
            return None

    async def _run_and_save_symbol_data(
        self,
        symbol: str,
        strategy: BaseSignalStrategy,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[pd.DataFrame]:
        """
        Runs backtest for a symbol with best params and saves the DataFrame, loading feature data if needed.
        start_date and end_date are only used for file naming and feature data loading, not passed to backtest_func.
        """
        try:
            # Load feature data for the symbol
            feature_data_loader = self.stage_data_loader.load_stage_data(
                symbol=symbol,
                stage=self.stage.input_stage,
                start_date=start_date,
                end_date=end_date,
                reverse_pages=True,
            )
            if feature_data_loader is None:
                self.logger.warning(
                    f"[PortfolioMatrixLoader] No feature data found for {symbol} in range {start_date} to {end_date}, skipping backtest."
                )
                return None
            # Run the backtest
            result: Dict[
                str, list[pd.DataFrame]
            ] = await self.executor.run_backtest_async(
                [strategy], {symbol: feature_data_loader}
            )
            self.logger.info(
                f"[PortfolioMatrixLoader] Backtest completed for {symbol} with strategy {strategy.__class__.__name__}."
            )
            if not result or not result.get(symbol):
                self.logger.warning(
                    f"[PortfolioMatrixLoader] Backtest returned empty DataFrame for {symbol}."
                )

            # Save the DataFrame to a Parquet file
            dfs = result.get(symbol, [])
            if not dfs:
                self.logger.warning(
                    f"[PortfolioMatrixLoader] Backtest returned empty DataFrame for {symbol}."
                )
                return
            if not isinstance(dfs, list):
                self.logger.error(
                    f"[PortfolioMatrixLoader] Backtest result for {symbol} is not a list of DataFrames: {dfs}"
                )
                return

            df = pd.concat(dfs, axis=0, ignore_index=True)
            if df.empty:
                self.logger.warning(
                    f"[PortfolioMatrixLoader] Backtest returned empty DataFrame for {symbol}."
                )
                return

            # Filter columns to only those needed downstream
            downstream_cols = [
                SignalStrategyExecutorColumns.ENTRY_SIGNAL,
                SignalStrategyExecutorColumns.EXIT_SIGNAL,
                SignalStrategyExecutorColumns.SYMBOL,
                SignalStrategyExecutorColumns.TIMESTAMP,
                SignalStrategyExecutorColumns.OPEN_PRICE,
                SignalStrategyExecutorColumns.HIGH_PRICE,
                SignalStrategyExecutorColumns.LOW_PRICE,
                SignalStrategyExecutorColumns.CLOSE_PRICE,
            ]
            # Only keep columns that exist in df
            filtered_cols = [col for col in downstream_cols if col in df.columns]
            df = df[filtered_cols]

            file_path = self._get_signal_file_path(symbol, start_date, end_date)
            df.to_parquet(file_path)

            self.stage_data_manager.mark_symbol_stage(
                stage=self.stage,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                statusExtension=DataExtension.DONE,
            )
            return
        except Exception as e:
            self.logger.error(
                f"[PortfolioMatrixLoader] Failed to run/save data for {symbol}: {e}"
            )
            return None

    def _get_signal_file_path(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Path:
        """
        Get the full path to the signal file for a symbol and date window.

        Args:
            symbol (str): The symbol.
            start_date (datetime): Start date.
            end_date (datetime): End date.

        Returns:
            Path: Full path to the signal file.
        """
        dir_path = Path(
            self.stage_data_manager.get_directory_path(
                base_dir=self.data_dir,
                stage=self.stage,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
        )
        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        return dir_path / self.symbol_signals_filename

    def _load_symbol_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[pd.DataFrame]:
        """
        Load the signal data for a symbol and date window.

        Args:
            symbol (str): The symbol.
            start_date (datetime): Start date.
            end_date (datetime): End date.

        Returns:
            Optional[pd.DataFrame]: The loaded DataFrame, or None if not found.
        """
        file_path = self._get_signal_file_path(symbol, start_date, end_date)
        if not file_path.exists():
            self.logger.warning(
                f"[PortfolioMatrixLoader] Data file not found for {symbol}: {file_path} (will exclude from matrix)"
            )
            return None
        return pd.read_parquet(file_path)

    def _get_optimized_strategy(
        self,
        symbol: str,
    ) -> Optional[BaseSignalStrategy]:
        """
        Uses stage_data_manager to resolve the symbol directory, loads evaluation_result.json, checks viability, and returns an initialized strategy instance or None.
        Logs key events if logger is provided.
        """
        try:
            optimized_strategy_summary = self._get_optimization_summary(
                symbol=symbol,
            )
            self.logger.debug(
                f"[PortfolioMatrixLoader] Loaded optimization summary for {symbol}: {optimized_strategy_summary}"
            )
            is_viable = optimized_strategy_summary.get("is_viable", False)
            if not is_viable:
                self.logger.info(
                    f"[PortfolioMatrixLoader] Symbol {symbol} is not viable based on optimization results."
                )
                return None
            strategy_name = optimized_strategy_summary.get("strategy")
            strategy_params = optimized_strategy_summary.get(
                "most_common_best_params", {}
            )
            strategy = SYMBOL_STRATEGY_CLASS_MAP.get(strategy_name)
            return self.strategy_factory.build_strategy(
                strategy_class=strategy, params=strategy_params
            )
        except Exception as e:
            self.logger.error(
                f"[PortfolioMatrixLoader] Error retrieving optimized strategy for {symbol}: {e}"
            )
            return None

    def _get_optimization_summary(self, symbol: str) -> Optional[Dict]:
        """
        Get optimization summary for a given strategy and symbol.

        Args:
            symbol (str): The symbol.

        Returns:
            Optional[Dict]: Optimization summary dictionary, or None if error.
        """
        try:
            json_path = self._get_optimization_result_path(symbol=symbol)
            self.logger.debug(
                f"Loading optimization summary from {json_path} for Symbol:{symbol}"
            )
            if not json_path.exists() or json_path.stat().st_size == 0:
                self.logger.warning(
                    f"No optimization summary for Symbol:{symbol} (optimization summary file does not exist or is empty)"
                )
                return {}
            with open(json_path, "r") as f:
                try:
                    opt_results = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"Optimization summary file {json_path} is not valid JSON. Returning empty dict."
                    )
                    return {}

            if opt_results is None:
                self.logger.warning(
                    f"No optimization summary for {symbol} (optimization summary file is empty)"
                )
                return {}
            self.logger.debug(f"Optimization summary for {symbol}: {opt_results}")
            if not isinstance(opt_results, dict):
                self.logger.warning(
                    f"Optimization summary for {symbol} is not a dictionary: {opt_results}"
                )
                return {}

            return opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving optimization summary for {symbol}: {e} (symbol: {symbol})"
            )
            return None

    def _get_optimization_result_path(self, symbol: Optional[str]) -> Path:
        """
        Get the path to the optimization result JSON file for a given strategy and symbol.

        Args:
            symbol (Optional[str]): The symbol.

        Returns:
            Path: Path to the optimization summary JSON file.
        """
        out_dir = Path(
            self.stage_data_manager.get_directory_path(
                base_dir=self.optimization_root,
                symbol=symbol,
            )
        )
        # Only create directory when saving, not when reading
        return out_dir / self.signal_summary_json_filename
