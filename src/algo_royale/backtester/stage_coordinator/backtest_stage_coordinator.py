from logging import Logger
from typing import AsyncIterator, Callable, Dict

import pandas as pd

from algo_royale.backtester.backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.backtester.watchlist.watchlist import load_watchlist
from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.config.config import Config
from algo_royale.strategy_factory.strategies.base_strategy import Strategy
from algo_royale.strategy_factory.strategy_factory import StrategyFactory


class BacktestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        config: Config,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_factory: StrategyFactory,
    ):
        super().__init__(
            stage=BacktestStage.BACKTEST,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        watchlist_path = config.get("paths.backtester", "watchlist_path", [])
        if not self.watchlist_path:
            raise ValueError("Watchlist path not specified in config")
        self.watchlist = load_watchlist(watchlist_path)
        if not self.watchlist:
            raise ValueError("Watchlist is empty or could not be loaded")
        self.strategy_factory = strategy_factory
        self.executor = StrategyBacktestExecutor(stage_data_manager, logger)

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Dict[None, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Run the backtest and return a dict mapping symbol to a factory that yields result DataFrames.
        """
        strategies: list[Strategy] = self.strategy_factory.all_strategy_combinations
        if not strategies:
            self.logger.error("No strategies found in the strategy factory.")
            return {}

        results: Dict[str, Dict[str, list[pd.DataFrame]]] = {}

        for symbol in self.watchlist:
            for strategies in strategies.items():
                if symbol not in prepared_data:
                    self.logger.warning(
                        f"No prepared data for symbol {symbol}, skipping."
                    )
                    continue

                self.logger.debug(f"Running backtest for symbol: {symbol}")
                symbol_results = await self.executor.run_backtest(
                    strategies, {symbol: prepared_data[symbol]}
                )
                # symbol_results: Dict[str, list[pd.DataFrame]], where key is symbol
                if symbol_results and symbol in symbol_results:
                    # For each strategy, collect its results
                    for strategy in strategies:
                        strategy_name = strategy.get_hash_id()
                        # Filter DataFrames for this strategy
                        strategy_dfs = (
                            [
                                df
                                for df in symbol_results[symbol]
                                if (
                                    StrategyColumns.STRATEGY_NAME in df.columns
                                    and (
                                        df[StrategyColumns.STRATEGY_NAME]
                                        == strategy_name
                                    ).any()
                                )
                            ]
                            if symbol_results[symbol]
                            else []
                        )
                        if symbol not in results:
                            results[symbol] = {}
                        results[symbol][strategy_name] = strategy_dfs
                else:
                    self.logger.warning(f"No results for symbol {symbol}.")

        if not results:
            self.logger.error("Backtest returned no results.")
            return {}

        # Convert results to a dict of async generators
        # where each symbol maps to a generator that yields DataFrames
        def make_factory(dfs):
            async def gen():
                for df in dfs:
                    if isinstance(df, pd.DataFrame):
                        # Ensure df is a DataFrame before yielding
                        yield df
                    else:
                        self.logger.warning(
                            f"Expected DataFrame, got {type(df)} for symbol."
                        )

            # Ensure the generator is async
            if not isinstance(dfs, list):
                self.logger.error(
                    f"Expected a list of DataFrames for symbol, got {type(dfs)}"
                )
                return
            # Return an async generator function for the DataFrame list
            return gen

        return {
            symbol: {
                strategy_name: make_factory(dfs)
                for strategy_name, dfs in strategy_dict.items()
            }
            for symbol, strategy_dict in results.items()
        }
