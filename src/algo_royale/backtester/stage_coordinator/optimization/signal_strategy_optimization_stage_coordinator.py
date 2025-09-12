import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactory,
)
from algo_royale.backtester.stage_coordinator.optimization.base_optimization_stage_coordinator import (
    BaseOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data_validation.signal_strategy_optimization_result_validator import (
    signal_strategy_optimization_validator,
)
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from algo_royale.logging.loggable import Loggable


class SignalStrategyOptimizationStageCoordinator(BaseOptimizationStageCoordinator):
    """Coordinator for the optimization stage of the backtest pipeline.
    This class is responsible for optimizing and backtesting strategies
    for a list of symbols using the provided data loader, data writer,
    and strategy executor.
    It also handles the evaluation of the backtest results.

    Parameters:
        data_loader: SymbolStrategyDataLoader instance for loading data.
        logger: Loggable instance for logging information and errors.
        stage_data_manager: StageDataManager instance for managing stage data.
        strategy_executor: StrategyBacktestExecutor instance for executing backtests.
        strategy_evaluator: BacktestEvaluator instance for evaluating backtest results.
        strategy_combinator_factory: SignalStrategyCombinatorFactory instance for creating strategy combinators.
        optimization_root: Root directory for saving optimization results.
        optimization_json_filename: Name of the JSON file to save optimization results.
        signal_strategy_optimizer_factory: Factory for creating signal strategy optimizers.
        optimization_n_trials: int = 1,
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        logger: Loggable,
        stage_data_manager: StageDataManager,
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_combinator_factory: SignalStrategyCombinatorFactory,
        optimization_root: str,
        optimization_json_filename: str,
        signal_strategy_optimizer_factory: SignalStrategyOptimizerFactory,
        optimization_n_trials: int = 1,
    ):
        super().__init__(
            stage=BacktestStage.STRATEGY_OPTIMIZATION,
            data_loader=data_loader,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.optimization_json_filename = optimization_json_filename
        self.signal_strategy_optimizer_factory = signal_strategy_optimizer_factory
        self.executor = strategy_executor
        self.evaluator = strategy_evaluator
        self.stage_data_manager = stage_data_manager
        self.optimization_n_trials = optimization_n_trials
        self.strategy_combinator_factory = strategy_combinator_factory

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """Process the data for optimization and backtesting.
        This method iterates over the data for each symbol, performing
        optimization and backtesting as needed.
        """

        results = {}
        for symbol, df_iter_factory in data.items():
            if symbol not in data:
                self.logger.warning(f"No data for symbol: {symbol}")
                continue

            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window for dates {self.start_date} to {self.end_date}"
                )
                continue
            train_df = pd.concat(dfs, ignore_index=True)

            for (
                strategy_combinator
            ) in self.strategy_combinator_factory.all_combinators():
                try:
                    strategy_class = strategy_combinator.strategy_class
                    strategy_name = strategy_class.__name__

                    if self._has_optimization_run(
                        symbol=symbol,
                        strategy_name=strategy_name,
                        start_date=self.start_date,
                        end_date=self.end_date,
                    ):
                        self.logger.info(
                            f"Skipping optimization for {symbol} {strategy_name} as it has already been run."
                        )
                        skip_result_json = {
                            strategy_name: {
                                "optimization": {
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

                    # Run optimization
                    optimizer = self.signal_strategy_optimizer_factory.create(
                        strategy_class=strategy_class,
                        condition_types=strategy_combinator.get_condition_types(),
                        backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                            symbol, strat, df_
                        ),
                    )
                    optimization_result = optimizer.optimize(
                        symbol=symbol,
                        df=train_df,
                        window_start_time=self.start_date,
                        window_end_time=self.end_date,
                        n_trials=self.optimization_n_trials,
                    )
                    # Fix: Use the correct validator for single result dicts
                    if (
                        isinstance(optimization_result, dict)
                        and "strategy" in optimization_result
                    ):
                        valid = signal_strategy_optimization_validator(
                            optimization_result, self.logger
                        )
                    else:
                        valid = self._validate_optimization_results(optimization_result)
                    if not valid:
                        self.logger.error(
                            f"[{self.stage}] Optimization results validation failed for {symbol} {strategy_name}"
                        )
                        continue
                    # Write the optimization results to JSON
                    results = self._write_results(
                        symbol=symbol,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        strategy_name=strategy_name,
                        optimization_result=optimization_result,
                        collective_results=results,
                    )
                except Exception as e:
                    self.logger.error(
                        f"Optimization failed for symbol {symbol}, strategy {strategy_name}: {e}"
                    )
                    continue

        return results

    def _has_optimization_run(
        self, symbol: str, strategy_name: str, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if optimization has already been run for the current stage, for the specific symbol, strategy, and window."""
        try:
            existing_optimization_json = self.get_existing_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            self.logger.debug(
                f"Checking existing optimization results for {symbol} {strategy_name} in window {self.window_id} | existing_optimization_json: {existing_optimization_json} "
            )

            # Check for the specific window_id in the JSON
            window_data = existing_optimization_json.get(self.window_id)
            if not window_data:
                self.logger.info(
                    f"No optimization data for window {self.window_id} for {symbol} {strategy_name}"
                )
                return False

            # Check for the presence of 'optimization' key and correct strategy name
            optimization = window_data.get("optimization")
            if not optimization:
                self.logger.info(
                    f"No optimization section for window {self.window_id} for {symbol} {strategy_name}"
                )
                return False
            if optimization.get("strategy") != strategy_name:
                self.logger.info(
                    f"Optimization strategy mismatch for window {self.window_id}: expected {strategy_name}, found {optimization.get('strategy')}"
                )
                return False

            # Optionally, check for symbol match in meta
            meta = optimization.get("meta", {})
            if meta.get("symbol") and meta.get("symbol") != symbol:
                self.logger.info(
                    f"Optimization symbol mismatch for window {self.window_id}: expected {symbol}, found {meta.get('symbol')}"
                )
                return False
            # Validate the structure of the optimization data
            if not self.stage.output_validation_fn(
                existing_optimization_json, self.logger
            ):
                self.logger.info(
                    f"Optimization data validation failed for {symbol} {strategy_name} in window {self.window_id}. Confirming that optimization has not been run."
                )
                return False
            self.logger.info(
                f"Optimization already run for {symbol} {strategy_name} in window {self.window_id}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Error checking optimization results for {symbol} {strategy_name} in window {self.window_id}: {e}"
            )
            return False

    def _get_output_path(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ):
        """Get the output path for the optimization results JSON file."""
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / self.optimization_json_filename

    async def _backtest_and_evaluate(
        self,
        symbol: str,
        strategy: BaseSignalStrategy,
        df: pd.DataFrame,
    ):
        # We wrap df into an async factory as your executor expects
        async def data_factory():
            yield df

        raw_results = await self.executor.run_backtest_async(
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

    def _validate_optimization_results(
        self, results: Dict[str, Dict[str, dict]]
    ) -> bool:
        """Validate the optimization results to ensure they contain the expected structure."""
        try:
            validation_method = self.stage.value.output_validation_fn
            if not validation_method:
                self.logger.warning(
                    "No validation method defined for strategy optimization results. Skipping validation."
                )
                return False
            return validation_method(results, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating optimization results: {e}. Results: {results}"
            )
            return False

    def _write_results(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy_name: str,
        optimization_result: Dict[str, Any],
        collective_results: Dict[str, Dict[str, dict]],
    ) -> Dict[str, Dict[str, dict]]:
        try:
            optimization_json = {
                self.window_id: {
                    "optimization": {
                        "strategy": strategy_name,
                        "best_value": optimization_result.get("best_value"),
                        "best_params": optimization_result.get("best_params", {}),
                        "meta": {
                            "run_time_sec": optimization_result.get("run_time_sec", 0),
                            "n_trials": optimization_result.get("n_trials", 0),
                            "symbol": symbol,
                            "direction": optimization_result.get("direction", "long"),
                            "multi_objective": optimization_result.get(
                                "multi_objective", False
                            ),
                        },
                        "metrics": optimization_result.get("metrics", {}),
                    },
                    "window": {
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "window_id": f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}",
                    },
                }
            }

            # Get existing results for the symbol and strategy
            existing_optimization_json = self.get_existing_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if existing_optimization_json is None:
                self.logger.warning(
                    f"No existing optimization results for {symbol} {strategy_name} {self.window_id}"
                )
                existing_optimization_json = {}

            updated_optimization_json = self._deep_merge(
                existing_optimization_json, optimization_json
            )
            # Save optimization metrics to optimization_result.json under window_id
            out_path = self._get_output_path(
                strategy_name,
                symbol,
                start_date,
                end_date,
            )
            self.logger.info(
                f"Saving optimization results for {symbol} {strategy_name} to {out_path} results: {updated_optimization_json}"
            )
            # Write the updated results to the file
            with open(out_path, "w") as f:
                json.dump(updated_optimization_json, f, indent=2, default=str)

            # Update the results dictionary to match the validator's requirements
            collective_results.setdefault(symbol, {})[strategy_name] = optimization_json
        except Exception as e:
            self.logger.error(
                f"Error writing results for {symbol} {strategy_name}: {e}"
            )
        return collective_results

    def get_existing_optimization_results(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, dict]:
        """Retrieve existing optimization results for a given strategy and symbol."""
        try:
            self.logger.info(
                f"Retrieving optimization results for {strategy_name} during {self.window_id}"
            )
            train_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if train_opt_results is None:
                self.logger.warning(
                    f"No optimization result for {symbol} {strategy_name} {self.window_id}"
                )
                return {}
            return train_opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving optimization results for {strategy_name} during {self.window_id}: {e}"
            )
            return None
