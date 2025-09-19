import asyncio
from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyExecutorColumns,
)
from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_manager import (
    StageDataManager,
)
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.logging.loggable import Loggable


class StrategyBacktestExecutor:
    def __init__(self, stage_data_manager: StageDataManager, logger: Loggable):
        self.logger = logger
        self.stage_data_manager = stage_data_manager
        self.stage = BacktestStage.SIGNAL_BACKTEST_EXECUTOR
        self._processed_pairs = set()

    async def run_backtest_async(
        self,
        strategies: list[BaseSignalStrategy],
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ) -> Dict[str, list[pd.DataFrame]]:
        """
        Run backtest for the given strategies and data.
        Includes robust exception handling and validation.
        """
        # Ensure results are initialized for all symbols
        results = {symbol: [] for symbol in data.keys()}

        if not data:
            self.logger.error("No data available - check your data paths and files")
            return results

        try:
            self.logger.info("Starting async backtest for strategies: %s", strategies)

            for symbol, async_iterator_factory in data.items():
                self.logger.debug(f"Processing symbol: {symbol} for all strategies")
                async_df_iterator = async_iterator_factory()
                page_count = 0

                async for page_df in async_df_iterator:
                    page_count += 1
                    for strategy in strategies:
                        strategy_name = strategy.get_hash_id()
                        pair_key = f"{symbol}_{strategy_name}"
                        self.logger.debug(
                            f"Processing page {page_count} for {symbol}-{strategy_name}"
                        )
                        if self._should_skip_pair(pair_key, strategy_name, symbol):
                            self.logger.debug(
                                f"Skipping {symbol}-{strategy_name} as already processed"
                            )
                            continue

                        try:
                            # Explicitly handle extreme values
                            self.logger.debug(
                                f"Page {page_count} before filtering: shape={page_df.shape}, columns={list(page_df.columns)}, head={page_df.head(2)}"
                            )
                            page_df = self._filter_extreme_values(page_df)
                            self.logger.debug(
                                f"Page {page_count} after filtering: shape={page_df.shape}, columns={list(page_df.columns)}, head={page_df.head(2)}"
                            )

                            # Ensure valid pages are processed
                            if page_df.empty:
                                self.logger.debug(
                                    f"Page {page_count} for {symbol}-{strategy_name} is empty after filtering extreme values. Skipping."
                                )
                                continue

                            result_df = await self._process_single_page(
                                symbol, strategy, page_df, page_count
                            )
                            # Ensure valid pages are appended correctly
                            if result_df is not None:
                                results[symbol].append(result_df)
                            else:
                                self.logger.warning(
                                    f"Page {page_count} for {symbol}-{strategy_name} resulted in None. Skipping."
                                )
                        except ValueError as ve:
                            self.logger.warning(
                                f"Validation error on page {page_count} for {symbol}-{strategy_name}: {str(ve)}"
                            )
                            continue
                        except Exception as e:
                            self.logger.error(
                                f"Error processing page {page_count} for {symbol}-{strategy_name}: {str(e)}",
                                exc_info=True,
                            )
                            continue

            return results
        except asyncio.CancelledError:
            self.logger.warning("Backtest cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Critical backtest failure: {e}")
            raise

    async def _process_single_page(
        self,
        symbol: str,
        strategy: BaseSignalStrategy,
        page_df: pd.DataFrame,
        page_num: int,
    ) -> pd.DataFrame:
        """Process a single page of data with proper signal handling"""
        strategy_name = strategy.get_hash_id()
        self.logger.debug(
            f"Processing page {page_num} for symbol: {symbol} with strategy: {strategy_name}"
        )
        if page_df.empty:
            self.logger.debug(
                f"Empty page {page_num} for symbol:{symbol} | strategy:{strategy_name}"
            )
            return pd.DataFrame(
                columns=[
                    SignalStrategyExecutorColumns.ENTRY_SIGNAL,
                    SignalStrategyExecutorColumns.EXIT_SIGNAL,
                    SignalStrategyExecutorColumns.STRATEGY_NAME,
                    SignalStrategyExecutorColumns.SYMBOL,
                ]
            )

        try:
            # Filter extreme values
            page_df = self._filter_extreme_values(page_df)
            self.logger.debug(
                f"Page {page_num} for {symbol}-{strategy_name} after filtering extreme values: shape={page_df.shape}, columns={list(page_df.columns)}, head={page_df.head(2)}"
            )
            # Ensure valid pages are processed and appended
            if page_df.empty:
                self.logger.warning(
                    f"Page {page_num} for {symbol}-{strategy_name} is empty after filtering. Skipping."
                )
                return pd.DataFrame(
                    columns=[
                        SignalStrategyExecutorColumns.ENTRY_SIGNAL,
                        SignalStrategyExecutorColumns.EXIT_SIGNAL,
                        SignalStrategyExecutorColumns.STRATEGY_NAME,
                        SignalStrategyExecutorColumns.SYMBOL,
                    ]
                )

            # Generate and validate signals
            try:
                self.logger.debug(
                    f"Generating signals for page {page_num} of {symbol}-{strategy_name}"
                )
                signals_df = strategy.generate_signals(page_df.copy())
                self.logger.debug(
                    f"Signals generated for page {page_num} of {symbol}-{strategy_name}: shape={signals_df.shape}, columns={list(signals_df.columns)}, head={signals_df.head(2)}"
                )
                self._validate_strategy_output(strategy, page_df, signals_df)
                self.logger.debug(
                    f"Page {page_num} for {symbol}-{strategy_name} signals validated successfully"
                )
            except Exception as e:
                self.logger.error(
                    f"Error generating signals for page {page_num} of {symbol}-{strategy_name}: {str(e)}"
                )
                return None

            # Create result DataFrame
            result_df = signals_df.copy()
            result_df[SignalStrategyExecutorColumns.STRATEGY_NAME] = strategy_name
            result_df[SignalStrategyExecutorColumns.SYMBOL] = symbol

            return result_df

        except Exception as e:
            self.logger.error(
                f"Critical error processing page {page_num} for {symbol}-{strategy_name}: {str(e)}"
            )
            return None

    def _should_skip_pair(self, pair_key: str, strategy_name: str, symbol: str) -> bool:
        if pair_key in self._processed_pairs:
            self.logger.info(
                f"Skipping already processed pair: {symbol}-{strategy_name}"
            )
            return True

        if self.stage_data_manager.is_symbol_stage_done(
            self.stage, strategy_name, symbol
        ):
            self.logger.info(
                f"Found existing results for {symbol}-{strategy_name}, skipping..."
            )
            self._processed_pairs.add(pair_key)
            return True

        return False

    def _validate_strategy_output(
        self, strategy: BaseSignalStrategy, df: pd.DataFrame, signals_df: pd.DataFrame
    ) -> None:
        """
        Validate the strategy output DataFrame for required columns, null values, and numerical stability.
        """
        strategy_name = strategy.get_hash_id()
        if len(signals_df) != len(df):
            self.logger.warning(
                f"Strategy {strategy_name} returned {len(signals_df)} rows for {len(df)} input rows"
            )

        if not isinstance(signals_df, pd.DataFrame):
            self.logger.warning(
                f"Strategy {strategy_name} must return a pandas DataFrame, got {type(signals_df)}"
            )

        # Ensure ENTRY_SIGNAL and EXIT_SIGNAL columns are numeric before .abs(), defaulting non-numeric/null to 0 (inaction)
        for col in [
            SignalStrategyExecutorColumns.ENTRY_SIGNAL,
            SignalStrategyExecutorColumns.EXIT_SIGNAL,
        ]:
            if col in signals_df.columns:
                signals_df[col] = pd.to_numeric(
                    signals_df[col], errors="coerce"
                ).fillna(0)

        if (
            signals_df[
                [
                    SignalStrategyExecutorColumns.ENTRY_SIGNAL,
                    SignalStrategyExecutorColumns.EXIT_SIGNAL,
                ]
            ]
            .abs()
            .max()
            > 1e6
        ).any():
            self.logger.warning(
                f"Strategy {strategy_name} returned extreme signal values (> 1e6). These will be skipped."
            )

    def _filter_extreme_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out rows with extreme values in the DataFrame. Now also logs and skips suspiciously large/small values.
        """
        if SignalStrategyExecutorColumns.CLOSE_PRICE in df.columns:
            null_rows = df[SignalStrategyExecutorColumns.CLOSE_PRICE].isnull()
            if not null_rows.empty:
                self.logger.debug(
                    f"Null close prices detected at indices: {null_rows.index.tolist()}. These rows will be skipped: {df[null_rows][SignalStrategyExecutorColumns.CLOSE_PRICE].tolist()}"
                )
            extreme_rows = df[SignalStrategyExecutorColumns.CLOSE_PRICE] > 1e6
            if extreme_rows.any():
                self.logger.warning(
                    f"Extreme close prices (> 1e6) detected at indices: {extreme_rows.index.tolist()}. These rows will be skipped: {df[extreme_rows][SignalStrategyExecutorColumns.CLOSE_PRICE].tolist()}"
                )

            invalid_rows = df[SignalStrategyExecutorColumns.CLOSE_PRICE] <= 0
            if invalid_rows.any():
                self.logger.debug(
                    f"Invalid close prices (<= 0) detected at indices: {invalid_rows.index.tolist()}. These rows will be skipped: {df[invalid_rows][SignalStrategyExecutorColumns.CLOSE_PRICE].tolist()}"
                )

            # Additional sanity checks
            suspiciously_large = df[SignalStrategyExecutorColumns.CLOSE_PRICE] > 1e8
            if suspiciously_large.any():
                self.logger.warning(
                    f"Suspiciously large close prices (> 1e8) detected at indices: {suspiciously_large.index.tolist()}. Values: {df[suspiciously_large][SignalStrategyExecutorColumns.CLOSE_PRICE].tolist()}"
                )
            suspiciously_small = df[SignalStrategyExecutorColumns.CLOSE_PRICE] < 0.01
            if suspiciously_small.any():
                self.logger.debug(
                    f"Suspiciously small close prices (< 0.01) detected at indices: {suspiciously_small.index.tolist()}. Values: {df[suspiciously_small][SignalStrategyExecutorColumns.CLOSE_PRICE].tolist()}"
                )

            # Retain only valid rows
            valid_rows = (
                ~extreme_rows & ~invalid_rows & ~null_rows & ~suspiciously_small
            )
            df = df[valid_rows]

        if df.empty:
            self.logger.debug(
                "DataFrame is empty after filtering extreme and invalid values."
            )

        return df
