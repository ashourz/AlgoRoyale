import asyncio
import inspect
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
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
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_factory: StrategyFactory,
        logger: Logger,
        strategy_combinators: Optional[Sequence[type[StrategyCombinator]]] = None,
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
        self.executor = strategy_executor
        self.evaluator = strategy_evaluator
        self.strategy_factory = strategy_factory

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
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
            self.logger.debug(f"Fetched {len(dfs)} dataframes for symbol: {symbol}")
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
        for symbol, strategy_name, dfs, optimization_result in results_list:
            try:
                if dfs:
                    results.setdefault(symbol, {})[strategy_name] = self.make_factory(
                        dfs
                    )
                    self.logger.info(
                        f"Backtest completed for {symbol} with {strategy_name}"
                    )
                else:
                    self.logger.warning(
                        f"No backtest results for {symbol} with {strategy_name}"
                    )
                    continue
                # Save optimization results if any
                self.data_writer.save_stage_data(
                    BacktestStage.STRATEGY_OPTIMIZATION,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    results_df=pd.DataFrame(
                        [optimization_result]
                    ),  # Note the brackets!
                    page_idx=0,
                )
            except Exception as e:
                self.logger.error(
                    f"Error processing results for {symbol} with {strategy_name}: {str(e)}"
                )
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
        data_factory: Callable[[], AsyncIterator[pd.DataFrame]],
    ) -> tuple[str, str, list[pd.DataFrame], dict]:
        """Optimize and backtest a strategy for a given symbol and data.
        Args:
            symbol: The stock symbol.
            df: The historical data as a DataFrame.
            strategy_combinator: The strategy combinator class.
            data_factory: Factory function to produce the data asynchronously.
        Returns:
            A tuple of (symbol, strategy_name, list of backtest result DataFrames).
        """
        try:
            # async def single_page_async_iter(df):
            #     yield df
            self.logger.info(
                f"Optimizing and backtesting for {symbol} with {strategy_combinator}"
            )
            optimizer = StrategyOptimizer(
                strategy_class=strategy_combinator.strategy_class,
                condition_types=strategy_combinator.get_condition_types(),
                # backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                #     [strat], {symbol: lambda: single_page_async_iter(df_)}
                # ),
                backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                    symbol, strat, df_
                ),
                logger=self.logger,
            )

            optimization_result = optimizer.optimize(symbol, df)
            self.logger.info(
                f"Optimization result for {symbol} with {strategy_combinator}: {optimization_result}"
            )
            best_params = optimization_result["best_params"]
            self.logger.info(f"Best params: {best_params}")

            # Instantiate best strategy

            # Only keep params accepted by the strategy's __init__
            valid_params = set(
                inspect.signature(
                    strategy_combinator.strategy_class.__init__
                ).parameters
            )
            filtered_params = {
                k: v
                for k, v in best_params.items()
                if k in valid_params and k != "self"
            }
            self.logger.info(f"Filtered params: {filtered_params}")

            # Use the factory to build the strategy with proper condition/stateful logic instantiation
            best_strategy = self.strategy_factory.build_strategy(
                strategy_combinator.strategy_class, filtered_params
            )

            # Run backtest with best strategy
            backtest_result = asyncio.run(
                self.executor.run_backtest([best_strategy], {symbol: data_factory})
            )
            dfs = backtest_result.get(symbol, [])

            # dfs = backtest_result.get(symbol, [])
            # optimization_results_df = pd.DataFrame(optimization_result)
            # # Instantiate evaluator (can be cached as self.evaluator if preferred)
            # evaluator = SimpleBacktestEvaluator(self.logger)
            # performance_metrics = {}

            # if dfs:
            #     # Usually one DataFrame per strategy; iterate or just evaluate the first for now
            #     performance_metrics = evaluator.evaluate(best_strategy, dfs[0])
            # return (symbol, optimization_result["strategy"], dfs)
            # return (symbol, optimization_result["strategy"], [optimization_results_df])
            return (symbol, optimization_result["strategy"], dfs, optimization_result)
        except Exception as e:
            self.logger.error(
                f"Error optimizing/backtesting for {symbol} with {strategy_combinator}: {str(e)}"
            )
            return (symbol, strategy_combinator.__name__, [])

    async def _backtest_and_evaluate(
        self,
        symbol: str,
        strategy: Strategy,
        df: pd.DataFrame,
    ):
        # We wrap df into an async factory as your executor expects
        async def data_factory():
            yield df

        raw_results = await self.executor.run_backtest(
            [strategy], {symbol: data_factory}
        )
        self.logger.debug(f"Raw backtest results: line count: {len(raw_results)}")
        dfs = raw_results.get(symbol, [])
        if not dfs:
            return {}
        self.logger.debug(f"Backtest result DataFrames: {len(dfs)}")
        full_df = pd.concat(dfs, ignore_index=True)
        metrics = self.evaluator.evaluate(strategy, full_df)
        return metrics
