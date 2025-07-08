import asyncio
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Union

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import (
    SignalStrategyExecutorColumns,
)
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.executor.base_backtest_executor import BacktestExecutor
from algo_royale.backtester.stage_data.stage_data_manager import (
    StageDataManager,
    mockStageDataManager,
)
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.logging.logger_singleton import mockLogger


class StrategyBacktestExecutor(BacktestExecutor):
    def __init__(self, stage_data_manager: StageDataManager, logger: Logger):
        self.logger = logger
        self.stage_data_manager = stage_data_manager
        self.stage = BacktestStage.SIGNAL_BACKTEST_EXECUTOR
        self._processed_pairs = set()

    async def run_backtest(
        self,
        strategies: list[BaseSignalStrategy],
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ) -> Dict[str, list[pd.DataFrame]]:
        """Pure async implementation for processing streaming data

        Returns a dictionary mapping symbols to lists of DataFrames containing backtest results.
        Each DataFrame corresponds to a strategy applied to the data for that symbol.
        """
        results = {}

        if not data:
            self.logger.error("No data available - check your data paths and files")
            return

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
                            result_df = await self._process_single_page(
                                symbol, strategy, page_df, page_count
                            )
                            if result_df is not None:
                                results.setdefault(symbol, []).append(result_df)
                        except Exception as e:
                            self.logger.error(
                                f"Error processing page {page_count} for {symbol}-{strategy_name}: {str(e)}"
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
    ) -> Union[pd.DataFrame, None]:
        """Process a single page of data with proper signal handling"""
        strategy_name = strategy.get_hash_id()
        if page_df.empty:
            self.logger.debug(
                f"Empty page {page_num} for symbol:{symbol} | strategy:{strategy_name}"
            )
            return None

        try:
            # Validate input data
            self._validate_data_quality(page_df)

            # Filter out rows with NaNs in required columns for this strategy
            required_cols = getattr(strategy, "required_columns", [])
            if required_cols:
                filtered_df = page_df.dropna(subset=required_cols)
            else:
                filtered_df = page_df

            if filtered_df.empty:
                self.logger.debug(
                    f"All rows dropped after filtering for required columns in page {page_num} for {symbol}-{strategy_name}"
                )
                return None
            # Generate and validate signals
            signals_df = strategy.generate_signals(page_df.copy())
            self.logger.debug(
                f"Generated signals: {type(signals_df)} with length {len(signals_df)}"
            )
            self._validate_strategy_output(strategy, page_df, signals_df)

            # Create result DataFrame
            result_df = signals_df.copy()
            result_df[SignalStrategyExecutorColumns.STRATEGY_NAME] = strategy_name
            result_df[SignalStrategyExecutorColumns.SYMBOL] = symbol

            return result_df

        except Exception as e:
            self.logger.error(
                f"Critical error processing page {page_num} for {symbol}-{strategy_name}: {str(e)}"
            )
            raise

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

    def _validate_data_quality(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Empty DataFrame received")

        # Only check essential columns for nulls
        essential_cols = [
            SignalStrategyExecutorColumns.TIMESTAMP,
            SignalStrategyExecutorColumns.CLOSE_PRICE,
        ]
        for col in essential_cols:
            if col not in df.columns:
                self.logger.error(f"Missing essential column: {col}")
                raise ValueError(f"Missing essential column: {col}")
            if df[col].isnull().any():
                self.logger.error(f"Null values found in essential column: {col}")
                raise ValueError(f"Null values found in essential column: {col}")

        if (df[SignalStrategyExecutorColumns.CLOSE_PRICE] <= 0).any():
            self.logger.error("Invalid close prices (<= 0) detected in DataFrame")
            raise ValueError("Invalid close prices (<= 0) detected")

        if not pd.api.types.is_datetime64_any_dtype(
            df[SignalStrategyExecutorColumns.TIMESTAMP]
        ):
            raise ValueError("Timestamp column must be datetime type")

    def _validate_strategy_output(
        self, strategy: BaseSignalStrategy, df: pd.DataFrame, signals_df: pd.DataFrame
    ) -> None:
        strategy_name = strategy.get_hash_id()
        if len(signals_df) != len(df):
            self.logger.error(
                f"Strategy {strategy_name} returned {len(signals_df)} rows for {len(df)} input rows"
            )
            raise ValueError(
                f"Strategy {strategy_name} returned "
                f"{len(signals_df)} rows for {len(df)} input rows"
            )

        if not isinstance(signals_df, pd.DataFrame):
            self.logger.error(
                f"Strategy {strategy_name} must return a pandas DataFrame, got {type(signals_df)}"
            )
            raise ValueError(f"Strategy {strategy_name} must return a pandas DataFrame")

        for col in [
            SignalStrategyExecutorColumns.ENTRY_SIGNAL,
            SignalStrategyExecutorColumns.EXIT_SIGNAL,
        ]:
            if col not in signals_df.columns:
                self.logger.error(
                    f"Strategy {strategy_name} output missing required column: {col}"
                )
                raise ValueError(
                    f"Strategy {strategy_name} output missing required column: {col}"
                )

        if (
            signals_df[
                [
                    SignalStrategyExecutorColumns.ENTRY_SIGNAL,
                    SignalStrategyExecutorColumns.EXIT_SIGNAL,
                ]
            ]
            .isnull()
            .any()
            .any()
        ):
            self.logger.error(
                f"Strategy {strategy_name} returned signals containing null values"
            )
            raise ValueError(
                f"Strategy {strategy_name} returned signals containing null values"
            )


def mockStrategyBacktestExecutor(data_dir: Path) -> StrategyBacktestExecutor:
    """
    Mock implementation of StrategyBacktestExecutor for testing purposes.
    """
    logger = mockLogger()
    stage_data_manager = mockStageDataManager(data_dir=data_dir)
    return StrategyBacktestExecutor(
        stage_data_manager=stage_data_manager, logger=logger
    )
