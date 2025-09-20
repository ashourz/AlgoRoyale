import inspect
import json
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enums.backtest_stage import BacktestStage
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
from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_factory import (
    SignalStrategyFactory,
)
from algo_royale.logging.loggable import Loggable


class SignalStrategyTestingStageCoordinator(BaseTestingStageCoordinator):
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
        strategy_combinator_factory (SignalStrategyCombinatorFactory): Factory to create strategy combinators.
        optimization_root (str): Root directory for saving optimization results.
        optimization_json_filename (str): Name of the JSON file to save optimization results.
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        stage_data_manager: StageDataManager,
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_factory: SignalStrategyFactory,
        logger: Loggable,
        strategy_combinator_factory: SignalStrategyCombinatorFactory,
        optimization_root: str,
        optimization_json_filename: str,
    ):
        super().__init__(
            data_loader=data_loader,
            stage_data_manager=stage_data_manager,
            stage=BacktestStage.STRATEGY_TESTING,
            logger=logger,
            evaluator=strategy_evaluator,
            optimization_root=optimization_root,
            optimization_json_filename=optimization_json_filename,
        )
        self.strategy_factory = strategy_factory
        self.strategy_combinator_factory = strategy_combinator_factory
        self.executor = strategy_executor

    def _get_train_optimization_results(
        self,
        strategy_name: str,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> Optional[Dict[str, Dict[str, dict]]]:
        """Retrieve train optimization results for a given strategy and window ID."""
        try:
            self.logger.info(
                f"Retrieving train optimization results for {strategy_name} during {self.train_window_id}"
            )
            train_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if not train_opt_results:
                self.logger.warning(
                    f"No train optimization result for {symbol} {strategy_name} {self.train_window_id}"
                )
                return {}
            return train_opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving train optimization results for {strategy_name} during {self.train_window_id}: {e}"
            )
            return None

    def _get_test_optimization_results(
        self,
        strategy_name: str,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> Optional[Dict[str, Dict[str, dict]]]:
        """Retrieve test optimization results for a given strategy and window ID."""
        try:
            self.logger.info(
                f"Retrieving test optimization results for {strategy_name} during {self.test_window_id}"
            )
            test_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if test_opt_results is None:
                self.logger.warning(
                    f"No test optimization result for {symbol} {strategy_name} {self.test_window_id}"
                )
                return {}
            return test_opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving test optimization results for {strategy_name} during {self.test_window_id}: {e}"
            )
            return None

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Run backtests for all strategies in the watchlist using the best parameters from optimization."""
        results = {}
        self.logger.debug(f"Initialized results dictionary: {results}")

        for symbol, df_iter_factory in data.items():
            self.logger.debug(f"Processing symbol: {symbol}")
            if symbol not in data:
                self.logger.warning(f"No data for symbol: {symbol}")
                continue

            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            self.logger.debug(f"DataFrames for {symbol}: {dfs}")
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window {self.train_window_id}"
                )
                continue
            test_df = pd.concat(dfs, ignore_index=True)
            self.logger.debug(f"Test DataFrame for {symbol}: {test_df}")
            for (
                strategy_combinator
            ) in self.strategy_combinator_factory.all_combinators():
                strategy_class = strategy_combinator.strategy_class
                strategy_name = strategy_class.__name__

                if self._has_optimization_run(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    start_date=self.test_start_date,
                    end_date=self.test_end_date,
                ):
                    self.logger.info(
                        f"Skipping optimization for {symbol} {strategy_name} as it has already been run."
                    )
                    skip_result_json = {
                        strategy_name: {
                            "test": {
                                "symbol": symbol,
                                "strategy": strategy_name,
                                "window_id": self.window_id,
                                "status": "skipped",
                                "reason": "Already run",
                            }
                        }
                    }
                    results = results | skip_result_json
                    continue

                self.logger.debug(f"Processing strategy: {strategy_name}")
                optimized_params = self._get_optimized_params(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    strategy_class=strategy_class,
                )
                self.logger.debug(
                    f"Optimized parameters for {strategy_name}: {optimized_params}"
                )
                if optimized_params is None:
                    self.logger.warning(
                        f"No optimized parameters found for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue
                strategy = self.strategy_factory.build_strategy(
                    strategy_class, optimized_params
                )

                async def data_factory():
                    yield test_df

                raw_results = await self.executor.async_run_backtest(
                    [strategy], {symbol: data_factory}
                )
                self.logger.debug(f"Raw results for {symbol}: {raw_results}")
                dfs = raw_results.get(symbol, [])
                if not dfs:
                    self.logger.warning(
                        f"No test results for {symbol} {strategy_name} {self.test_window_id}"
                    )
                    continue
                full_df = pd.concat(dfs, ignore_index=True)
                self.logger.debug(f"Full DataFrame for {symbol}: {full_df}")
                metrics = self.evaluator.evaluate(strategy, full_df)

                required_metrics = [
                    "total_return",
                    "sharpe_ratio",
                    "win_rate",
                    "max_drawdown",
                ]
                metrics = {k: metrics.get(k, 0.0) for k in required_metrics}
                self.logger.debug(f"Metrics for {strategy_name}: {metrics}")

                test_opt_results = self._get_test_optimization_results(
                    strategy_name,
                    symbol,
                    self.test_start_date,
                    self.test_end_date,
                )
                self.logger.debug(
                    f"Test optimization results for {strategy_name}: {test_opt_results}"
                )
                if test_opt_results is None:
                    self.logger.error(
                        f"Test results validation failed for {symbol} {strategy_name} {self.test_window_id}"
                    )
                    continue
                self.logger.debug(f"Metrics before writing: {metrics}")
                self.logger.debug(f"Test optimization results: {test_opt_results}")
                self.logger.debug(f"Results dictionary before writing: {results}")

                updated_results = self._write_test_results(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    metrics=metrics,
                    optimization_result=test_opt_results,
                    collective_results=results,
                )

                self.logger.debug(
                    f"Updated results from _write_test_results: {updated_results}"
                )
                results.update(updated_results)  # Fix merging logic
                self.logger.debug(f"Results dictionary after writing: {results}")

        self.logger.debug(f"Final results dictionary: {results}")
        return results

    def get_existing_optimization_results(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, dict]:
        """Retrieve existing optimization results for a given strategy and symbol."""
        try:
            self.logger.info(
                f"Retrieving optimization results for {strategy_name} during start date {start_date} and end date {end_date}"
            )
            train_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if train_opt_results is None:
                self.logger.warning(
                    f"No optimization result for {symbol} {strategy_name} during start date {start_date} and end date {end_date}"
                )
                return {}
            return train_opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving optimization results for {strategy_name} during start date {start_date} and end date {end_date}: {e}"
            )
            return None

    def _has_optimization_run(
        self, symbol: str, strategy_name: str, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if test has already been run for the current stage and test window."""
        try:
            existing_optimization_json = self.get_existing_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            # Check for the specific test window in the JSON
            test_data = existing_optimization_json.get(self.test_window_id)
            if not test_data:
                self.logger.info(
                    f"No test data for window {self.test_window_id} for {symbol} {strategy_name}"
                )
                return False
            # Check for the presence of 'test' key and metrics
            test_section = test_data.get("test")
            if not test_section or not test_section.get("metrics"):
                self.logger.info(
                    f"No test metrics for window {self.test_window_id} for {symbol} {strategy_name}"
                )
                return False
            # Validate the structure of the test data
            if not self.stage.output_validation_fn(test_data, self.logger):
                self.logger.info(
                    f"Test data validation failed for {symbol} {strategy_name} in window {self.test_window_id}. Confirming that optimization has not been run."
                )
                return False
            self.logger.info(
                f"Test already run for {symbol} {strategy_name} in window {self.test_window_id}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Error checking test run for {symbol} {strategy_name}: {e}"
            )
            return False

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
            train_opt_results = self._get_train_optimization_results(
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
            self.logger.debug(
                f"Validating optimization results for {symbol} {strategy_name} {self.train_window_id} | Results: {train_opt_results}"
            )
            if not self._validate_optimization_results(train_opt_results):
                self.logger.error(
                    f"[{self.stage}] Optimization results validation failed for {symbol} {strategy_name} {self.train_window_id}"
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
        try:
            validation_method = self.stage.value.input_validation_fn
            if not validation_method:
                self.logger.warning(
                    "No validation method defined for strategy optimization results. Skipping validation."
                )
                return False
            return validation_method(results, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating optimization results for {self.train_window_id}: {e}"
            )
            return False

    def _validate_test_results(
        self,
        results: Dict[str, Dict[str, dict]],
    ) -> bool:
        """Validate the test results to ensure they contain the expected structure."""
        try:
            validation_method = self.stage.value.output_validation_fn
            if not validation_method:
                self.logger.warning(
                    "No validation method defined for strategy test results. Skipping validation."
                )
                return False
            return validation_method(results, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating test results for {self.test_window_id}: {e}"
            )
            return False

    def _write_test_results(
        self,
        symbol: str,
        strategy_name: str,
        metrics: Dict[str, float],
        optimization_result: Dict[str, Any],
        collective_results: Dict[str, Dict[str, dict]],
    ) -> Dict[str, Dict[str, dict]]:
        try:
            self.logger.debug(
                f"Writing test results for symbol: {symbol}, strategy: {strategy_name}"
            )
            self.logger.debug(f"Metrics: {metrics}")
            self.logger.debug(
                f"Optimization result before update: {optimization_result}"
            )

            # Ensure metrics contain required keys with default values
            required_metrics = [
                "total_return",
                "sharpe_ratio",
                "win_rate",
                "max_drawdown",
            ]
            metrics = {k: metrics.get(k, 0.0) for k in required_metrics}

            # Update the optimization result dictionary
            test_optimization_json = {
                self.test_window_id: {
                    "test": {
                        "metrics": metrics,
                    },
                    "window": {
                        "start_date": self.test_start_date.strftime("%Y-%m-%d"),
                        "end_date": self.test_end_date.strftime("%Y-%m-%d"),
                        "window_id": self.test_window_id,
                    },
                }
            }

            updated_optimization_json = self._deep_merge(
                test_optimization_json, optimization_result
            )

            self.logger.debug(
                f"Optimization result after update: {updated_optimization_json}"
            )

            # Save the updated optimization results to the file
            test_opt_results_path = self._get_optimization_result_path(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=self.test_start_date,
                end_date=self.test_end_date,
            )
            self.logger.info(
                f"Saving test results for {strategy_name} and symbol {symbol} to {test_opt_results_path}"
            )
            with open(test_opt_results_path, "w") as f:
                json.dump(updated_optimization_json, f, indent=2, default=str)

            # Update the results dictionary
            collective_results.setdefault(symbol, {}).setdefault(
                strategy_name, {}
            ).setdefault(self.test_window_id, {})
            collective_results[symbol][strategy_name][self.test_window_id] = {
                "metrics": metrics,
            }
        except Exception as e:
            self.logger.error(
                f"Error writing test results for {strategy_name} during {self.test_window_id}: {e}"
            )
        return collective_results
