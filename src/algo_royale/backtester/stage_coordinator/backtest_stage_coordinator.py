import asyncio
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
        if not watchlist_path:
            raise ValueError("Watchlist path not specified in config")
        self.watchlist = load_watchlist(watchlist_path)
        if not self.watchlist:
            raise ValueError("Watchlist is empty or could not be loaded")
        self.strategy_factory = strategy_factory
        self.executor = StrategyBacktestExecutor(stage_data_manager, logger)

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """Process the backtest stage by running all strategies on the prepared data.
        Args:
            prepared_data (Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]):
                A dictionary where keys are symbols and values are async generators
                that yield DataFrames containing prepared data for each symbol.
        Returns:
            Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        self.logger.info("Starting backtest stage processing...")

        # Get all strategy combination lambdas and instantiate all strategies
        strategy_lambdas = self.strategy_factory.get_all_strategy_combination_lambdas()
        strategies = []
        for lambda_ in strategy_lambdas:
            strategies.extend(lambda_())

        if not strategies:
            self.logger.error("No strategies found in the strategy factory.")
            return {}
        else:
            self.logger.info(f"Found {len(strategies)} strategies to run.")

        results: Dict[str, Dict[str, list[pd.DataFrame]]] = {}
        semaphore = asyncio.Semaphore(100)  # Limit to 100 concurrent tasks

        async def process_symbol_strategy(symbol, strategy):
            async with semaphore:
                try:
                    if symbol not in prepared_data:
                        self.logger.warning(
                            f"No prepared data for symbol {symbol}, skipping."
                        )
                        return symbol, strategy.get_hash_id(), []

                    symbol_results = await self.executor.run_backtest(
                        [strategy], {symbol: prepared_data[symbol]}
                    )
                    strategy_name = strategy.get_hash_id()
                    strategy_dfs = (
                        [
                            df
                            for df in symbol_results.get(symbol, [])
                            if (
                                StrategyColumns.STRATEGY_NAME in df.columns
                                and (
                                    df[StrategyColumns.STRATEGY_NAME] == strategy_name
                                ).any()
                            )
                        ]
                        if symbol_results and symbol in symbol_results
                        else []
                    )
                    return symbol, strategy_name, strategy_dfs
                except Exception as e:
                    self.logger.error(
                        f"Error processing symbol {symbol} with strategy {strategy.get_hash_id()}: {e}"
                    )
                    return symbol, strategy.get_hash_id(), []

        # --- CONCURRENT EXECUTION ---
        tasks = [
            process_symbol_strategy(symbol, strategy)
            for symbol in self.watchlist
            for strategy in strategies
        ]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results, skipping exceptions
        for item in completed:
            if isinstance(item, Exception):
                self.logger.error(f"Exception in task: {item}", exc_info=True)
                continue
            if item is None:
                continue
            symbol, strategy_name, strategy_dfs = item
            if symbol not in results:
                results[symbol] = {}
            results[symbol][strategy_name] = strategy_dfs

        # Convert results to a dict of async generators
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
