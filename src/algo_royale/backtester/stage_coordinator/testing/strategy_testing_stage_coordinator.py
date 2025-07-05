import inspect
import json
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.stage_coordinator.testing.base_testing_stage_coordinator import (
    BaseTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.backtester.strategy_factory.signal.strategy_factory import (
    StrategyFactory,
)


class StrategyTestingStageCoordinator(BaseTestingStageCoordinator):
    """Coordinator for the strategy testing stage of the backtest pipeline.
    This class is responsible for testing strategies using the provided data loader,
    data preparer, and executor. It handles the evaluation of backtest results and manages
    optimization results for strategies.

    Parameters:
        data_loader (SymbolStrategyDataLoader): Loader for stage data.
        data_preparer (StageDataPreparer): Preparer for stage data.
        stage_data_manager (StageDataManager): Manager for stage data directories.
        strategy_executor (StrategyBacktestExecutor): Executor for running strategy backtests.
        strategy_evaluator (BacktestEvaluator): Evaluator for assessing strategy backtest results.
        strategy_factory (StrategyFactory): Factory for creating strategies.
        logger (Logger): Logger for logging information and errors.
        strategy_combinators (Sequence[type[SignalStrategyCombinator]]): List of strategy combinators.
        optimization_root (str): Root directory for saving optimization results.
        optimization_json_filename (str): Name of the JSON file to save optimization results.
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        data_preparer: StageDataPreparer,
        stage_data_manager: StageDataManager,
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_factory: StrategyFactory,
        logger: Logger,
        strategy_combinators: Sequence[type[SignalStrategyCombinator]],
        optimization_root: str,
        optimization_json_filename: str,
    ):
        super().__init__(
            data_loader=data_loader,
            data_preparer=data_preparer,
            stage_data_manager=stage_data_manager,
            stage=BacktestStage.STRATEGY_TESTING,
            logger=logger,
            executor=strategy_executor,
            evaluator=strategy_evaluator,
            strategy_combinators=strategy_combinators,
            optimization_root=optimization_root,
            optimization_json_filename=optimization_json_filename,
        )
        self.strategy_factory = strategy_factory

    async def _process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Run backtests for all strategies in the watchlist using the best parameters from optimization."""
        print(f"Prepared data: {prepared_data}")
        results = {}

        for symbol, df_iter_factory in prepared_data.items():
            print(f"Processing symbol: {symbol}")
            if symbol not in prepared_data:
                self.logger.warning(f"No prepared data for symbol: {symbol}")
                continue

            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            print(f"DataFrames for {symbol}: {dfs}")
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window {self.train_window_id}"
                )
                continue
            test_df = pd.concat(dfs, ignore_index=True)
            print(f"Test DataFrame for {symbol}: {test_df}")
            for strategy_combinator in self.strategy_combinators:
                strategy_class = strategy_combinator.strategy_class
                strategy_name = strategy_class.__name__
                train_opt_results = self._get_optimization_results(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    start_date=self.train_start_date,
                    end_date=self.train_end_date,
                )
                print(
                    f"Optimization results for {symbol} {strategy_name}: {train_opt_results}"
                )
                if not train_opt_results:
                    self.logger.warning(
                        f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue

                if (
                    self.train_window_id not in train_opt_results
                    or "optimization" not in train_opt_results[self.train_window_id]
                ):
                    self.logger.warning(
                        f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue

                best_params = train_opt_results[self.train_window_id]["optimization"][
                    "best_params"
                ]
                # Only keep params accepted by the strategy's __init__
                valid_params = set(
                    inspect.signature(strategy_class.__init__).parameters
                )
                filtered_params = {
                    k: v
                    for k, v in best_params.items()
                    if k in valid_params and k != "self"
                }
                self.logger.info(f"Filtered params: {filtered_params}")
                # Instantiate strategy and run backtest
                strategy = self.strategy_factory.build_strategy(
                    strategy_class, filtered_params
                )

                async def data_factory():
                    yield test_df

                raw_results = await self.executor.run_backtest(
                    [strategy], {symbol: data_factory}
                )
                dfs = raw_results.get(symbol, [])
                if not dfs:
                    self.logger.warning(
                        f"No test results for {symbol} {strategy_name} {self.test_window_id}"
                    )
                    continue
                full_df = pd.concat(dfs, ignore_index=True)
                metrics = self.evaluator.evaluate(strategy, full_df)

                test_opt_results = self._get_optimization_results(
                    strategy_name,
                    symbol,
                    self.test_start_date,
                    self.test_end_date,
                )
                # Save test metrics to optimization_result.json under window_id
                if self.test_window_id not in test_opt_results:
                    test_opt_results[self.test_window_id] = {}

                test_opt_results[self.test_window_id]["test"] = {"metrics": metrics}

                test_opt_results_path = self._get_optimization_result_path(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    start_date=self.test_start_date,
                    end_date=self.test_end_date,
                )

                with open(test_opt_results_path, "w") as f:
                    json.dump(test_opt_results, f, indent=2, default=str)

                results.setdefault(symbol, {})[strategy_name] = {
                    self.test_window_id: metrics
                }
                print(f"Raw results: {raw_results}")
                print(f"Metrics: {metrics}")
                print(f"Results so far: {results}")
        print(f"Final results: {results}")
        return results

    def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[str, Dict[str, Dict[str, float]]],
    ) -> None:
        """
        No-op: writing is handled in process().
        """
        self.logger.info(f"Processed data for stage {stage} is ready, but not written.")
        # Writing is handled in _process() where optimization results are saved
