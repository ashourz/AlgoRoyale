import inspect
import json
from logging import Logger
from typing import Any, AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

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
    data manager, and executor. It handles the evaluation of backtest results and manages
    optimization results for strategies.

    Parameters:
        data_loader (SymbolStrategyDataLoader): Loader for stage data.
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

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Run backtests for all strategies in the watchlist using the best parameters from optimization."""
        results = {}

        for symbol, df_iter_factory in data.items():
            print(f"Processing symbol: {symbol}")
            if symbol not in data:
                self.logger.warning(f"No data for symbol: {symbol}")
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
                # Get optimized parameters for the strategy
                optimized_params = self._get_optimized_params(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    strategy_class=strategy_class,
                )
                if optimized_params is None:
                    self.logger.warning(
                        f"No optimized parameters found for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue
                # Instantiate strategy and run backtest
                strategy = self.strategy_factory.build_strategy(
                    strategy_class, optimized_params
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
                # Get test optimization results
                test_opt_results = self._get_optimization_results(
                    strategy_name,
                    symbol,
                    self.test_start_date,
                    self.test_end_date,
                )
                # Validate test results
                if not self._validate_test_results(test_opt_results):
                    self.logger.error(
                        f"Test results validation failed for {symbol} {strategy_name} {self.test_window_id}"
                    )
                    continue
                # Write test results to optimization results
                results = self._write_test_results(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    metrics=metrics,
                    optimization_result=test_opt_results,
                    results=results,
                )
        return results

    def _get_optimized_params(
        self,
        symbol: str,
        strategy_name: str,
        strategy_class: type,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve optimized parameters for a given strategy and window ID."""
        try:
            self.logger.info(
                f"Retrieving optimized parameters for {strategy_name} during {self.train_window_id}"
            )
            train_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=self.train_start_date,
                end_date=self.train_end_date,
            )
            if not train_opt_results:
                self.logger.warning(
                    f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                )
                return None
            # validate the optimization results
            if not self._validate_optimization_results(train_opt_results):
                self.logger.error(
                    f"Optimization results validation failed for {symbol} {strategy_name} {self.train_window_id}"
                )
                return None
            if (
                self.train_window_id not in train_opt_results
                or "optimization" not in train_opt_results[self.train_window_id]
            ):
                self.logger.warning(
                    f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                )
                return None

            best_params = train_opt_results[self.train_window_id]["optimization"][
                "best_params"
            ]
            # Only keep params accepted by the strategy's __init__
            valid_params = set(inspect.signature(strategy_class.__init__).parameters)
            filtered_params = {
                k: v
                for k, v in best_params.items()
                if k in valid_params and k != "self"
            }
            self.logger.info(f"Filtered params: {filtered_params}")
            return filtered_params
        except Exception as e:
            self.logger.error(
                f"Error retrieving optimized parameters for {strategy_name} during {self.train_window_id}: {e}"
            )
            return None

    def _validate_optimization_results(
        self,
        results: Dict[str, Dict[str, dict]],
    ) -> bool:
        """Validate the optimization results to ensure they contain the expected structure."""
        validation_method = BacktestStage.STRATEGY_TESTING.value.input_validation_fn
        if not validation_method:
            self.logger.warning(
                "No validation method defined for strategy optimization results. Skipping validation."
            )
            return False
        return validation_method(results)

    def _validate_test_results(
        self,
        results: Dict[str, Dict[str, dict]],
    ) -> bool:
        """Validate the test results to ensure they contain the expected structure."""
        validation_method = BacktestStage.STRATEGY_TESTING.value.output_validation_fn
        if not validation_method:
            self.logger.warning(
                "No validation method defined for strategy test results. Skipping validation."
            )
            return False
        return validation_method(results)

    def _write_test_results(
        self,
        symbol: str,
        strategy_name: str,
        metrics: Dict[str, float],
        optimization_result: Dict[str, Any],
        results: Dict[str, Dict[str, dict]],
    ) -> Dict[str, Dict[str, dict]]:
        try:
            # Save test metrics to optimization_result.json under window_id
            if self.test_window_id not in optimization_result:
                optimization_result[self.test_window_id] = {}

            optimization_result[self.test_window_id]["test"] = {"metrics": metrics}

            test_opt_results_path = self._get_optimization_result_path(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=self.test_start_date,
                end_date=self.test_end_date,
            )

            with open(test_opt_results_path, "w") as f:
                json.dump(optimization_result, f, indent=2, default=str)

            results.setdefault(symbol, {})[strategy_name] = {
                self.test_window_id: metrics
            }
        except Exception as e:
            self.logger.error(
                f"Error writing test results for {strategy_name} during {self.test_window_id}: {e}"
            )
        return results
