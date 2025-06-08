import asyncio
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

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
from algo_royale.config.config import Config
from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.optimizer.strategy_optimizer import StrategyOptimizer


class BacktestStageCoordinator(StageCoordinator):
    def __init__(
        self,
        config: Config,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_combinators: Optional[list[type[StrategyCombinator]]] = None,
    ):
        """Coordinator for the backtest stage.
        Args:
            config: Configuration object.
            data_loader: Data loader for the stage.
            data_preparer: Data preparer for the stage.
            data_writer: Data writer for the stage.
            stage_data_manager: Stage data manager.
            logger: Logger instance.
            strategy_combinators: List of strategy combinator classes to use.
        """
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
        self.strategy_combinators = strategy_combinators
        if not self.strategy_combinators:
            raise ValueError("No strategy combinators provided")
        self.executor = StrategyBacktestExecutor(stage_data_manager, logger)

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[None, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        results = {}
        tasks = []

        for symbol in self.watchlist:
            if symbol not in prepared_data:
                self.logger.warning(f"No prepared data for symbol: {symbol}")
                continue

            # Fetch and cache data once per symbol
            dfs: list[pd.DataFrame] = []
            async for df in prepared_data[symbol]():
                dfs.append(df)
            df: pd.DataFrame = pd.concat(dfs, ignore_index=True)

            for strategy_combinator in self.strategy_combinators:
                task = asyncio.to_thread(
                    self._optimize_and_backtest,
                    symbol,
                    df,
                    strategy_combinator,
                    prepared_data[symbol],  # Pass factory to re-run async
                )
                tasks.append(task)

        results_list = await asyncio.gather(*tasks)

        # Collect results into proper structure
        for symbol, strategy_name, dfs in results_list:
            if dfs:
                results.setdefault(symbol, {})[strategy_name] = self.make_factory(dfs)

        return results

    def make_factory(
        self,
        dfs: list[pd.DataFrame],
    ) -> Callable[[], AsyncIterator[pd.DataFrame]]:
        """Creates a factory that yields the given list of DataFrames asynchronously."""

        async def factory() -> AsyncIterator[pd.DataFrame]:
            for df in dfs:
                yield df

        return factory

    def _optimize_and_backtest(
        self,
        symbol: str,
        df: pd.DataFrame,
        strategy_combinator: type[StrategyCombinator],
        data_factory,
    ) -> tuple[str, str, list[pd.DataFrame]]:
        """Optimize and backtest a strategy for a given symbol and data.
        Args:
            symbol: The stock symbol.
            df: The historical data as a DataFrame.
            strategy_combinator: The strategy combinator class.
            data_factory: Factory function to produce the data asynchronously.
        Returns:
            A tuple of (symbol, strategy_name, list of backtest result DataFrames).
        """
        optimizer = StrategyOptimizer(
            strategy_class=strategy_combinator.strategy_class,
            condition_types=strategy_combinator.get_condition_types(),
            backtest_fn=lambda strat, df_: self.executor.run_backtest(
                [strat], {symbol: lambda: iter([df_])}
            ),
            logger=self.logger,
        )

        optimization_result = optimizer.optimize(symbol, df, n_trials=50)
        # Rebuild and re-run with best config
        best_strategy = strategy_combinator(**optimization_result["best_params"])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        backtest_result = loop.run_until_complete(
            self.executor.run_backtest([best_strategy], {symbol: data_factory})
        )
        dfs = backtest_result.get(symbol, [])
        return (symbol, optimization_result["strategy"], dfs)
