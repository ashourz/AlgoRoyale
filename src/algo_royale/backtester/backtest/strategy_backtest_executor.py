import asyncio
from logging import Logger
from typing import AsyncIterator, Callable, Dict, List, Union

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.base_strategy import Strategy


class StrategyBacktestExecutor:
    def __init__(self, stage_data_manager: StageDataManager, logger: Logger):
        self.logger = logger
        self.stage_data_manager = stage_data_manager
        self.stage = BacktestStage.BACKTEST
        self._processed_pairs = set()

    async def run_backtest(
        self,
        strategies: List[Strategy],
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ) -> Dict[str, List[pd.DataFrame]]:
        """Pure async implementation for processing streaming data"""
        results = {}

        if not data:
            self.logger.error("No data available - check your data paths and files")
            return

        # Verify at least some files exist
        for symbol in data.keys():
            data_path = self.stage_data_manager.get_directory_path(
                self.stage, None, symbol
            )
            if not data_path.exists():
                self.logger.error(f"Data path does not exist: {data_path}")
            elif not any(data_path.glob("*.csv")):
                self.logger.error(f"No CSV files found in {data_path}")

        try:
            self.logger.info("Starting async backtest for strategies: %s", strategies)

            for symbol, async_iterator_factory in data.items():
                self.logger.debug(f"Processing symbol: {symbol} for all strategies")
                async_df_iterator = async_iterator_factory()
                page_count = 0

                async for page_df in async_df_iterator:
                    page_count += 1
                    for strategy in strategies:
                        strategy_name = strategy.get_directory()
                        pair_key = f"{symbol}_{strategy_name}"

                        if self._should_skip_pair(pair_key, strategy_name, symbol):
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
        self, symbol: str, strategy: Strategy, page_df: pd.DataFrame, page_num: int
    ) -> Union[pd.DataFrame, None]:
        """Process a single page of data with proper signal handling"""
        strategy_name = strategy.get_directory()
        if page_df.empty:
            self.logger.debug(
                f"Empty page {page_num} for symbol:{symbol} | strategy:{strategy_name}"
            )
            return None

        try:
            # Validate input data
            self._validate_data_quality(page_df)

            # Generate and validate signals
            signals = strategy.generate_signals(page_df.copy())
            self.logger.debug(
                f"Generated signals: {type(signals)} with length {len(signals)}"
            )
            self._validate_strategy_output(strategy, page_df, signals)

            # Create result DataFrame
            result_df = page_df.copy()
            result_df[StrategyColumns.SIGNAL] = (
                signals.values
            )  # Important: use .values to avoid issues with Series alignment
            result_df[StrategyColumns.STRATEGY_NAME] = strategy_name
            result_df[StrategyColumns.SYMBOL] = symbol

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

        if df.isnull().any().any():
            missing = df.columns[df.isnull().any()].tolist()
            raise ValueError(f"Data contains null values in columns: {missing}")

        if (df[StrategyColumns.CLOSE_PRICE] <= 0).any():
            raise ValueError("Invalid close prices (<= 0) detected")

        if not pd.api.types.is_datetime64_any_dtype(df[StrategyColumns.TIMESTAMP]):
            raise ValueError("Timestamp column must be datetime type")

    def _validate_strategy_output(
        self, strategy: Strategy, df: pd.DataFrame, signals: pd.Series
    ) -> None:
        strategy_name = strategy.get_directory()
        if len(signals) != len(df):
            raise ValueError(
                f"Strategy {strategy_name} returned "
                f"{len(signals)} signals for {len(df)} rows"
            )

        if not isinstance(signals, pd.Series):
            raise ValueError(f"Strategy {strategy_name} must return pandas Series")

        if signals.isnull().any():
            raise ValueError(
                f"Strategy {strategy_name} returned signals containing null values"
            )
