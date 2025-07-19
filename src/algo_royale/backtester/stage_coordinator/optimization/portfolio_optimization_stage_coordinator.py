import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactory,
)
from algo_royale.backtester.stage_coordinator.optimization.base_optimization_stage_coordinator import (
    BaseOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class PortfolioOptimizationStageCoordinator(BaseOptimizationStageCoordinator):
    """
    Coordinator for the portfolio optimization stage of the backtest pipeline.
    Optimizes portfolio strategies for a list of symbols using the provided data loader, data preparer, data writer, and optimizer.
    Params:
        data_loader (StageDataLoader): Loader for stage data.
        stage_data_manager (StageDataManager): Manages stage data paths and directories.
        logger (Logger): Logger for debugging and information.
        strategy_combinators (Sequence[type[PortfolioStrategyCombinator]]): List of strategy combinators to generate strategy combinations.
        executor (PortfolioBacktestExecutor): Executor to run backtests for portfolio strategies.
        evaluator (PortfolioBacktestEvaluator): Evaluator to assess backtest results.
        optimization_root (str): Root directory for optimization results.
        optimization_json_filename (str): Name of the JSON file to write optimization results.
        asset_matrix_preparer (AssetMatrixPreparer): Prepares asset-matrix form for portfolio strategies.
        portfolio_strategy_optimizer_factory (PortfolioStrategyOptimizerFactory): Factory to create portfolio strategy optimizers.
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        stage_data_manager: StageDataManager,
        logger: Loggable,
        strategy_combinators: Sequence[type[PortfolioStrategyCombinator]],
        executor: PortfolioBacktestExecutor,
        evaluator: PortfolioBacktestEvaluator,
        optimization_root: str,
        optimization_json_filename: str,
        asset_matrix_preparer: AssetMatrixPreparer,
        portfolio_strategy_optimizer_factory: PortfolioStrategyOptimizerFactory,
        strategy_debug: bool = False,
    ):
        super().__init__(
            stage=BacktestStage.PORTFOLIO_OPTIMIZATION,
            data_loader=data_loader,
            stage_data_manager=stage_data_manager,
            strategy_combinators=strategy_combinators,
            logger=logger,
        )
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.optimization_json_filename = optimization_json_filename
        self.asset_matrix_preparer = asset_matrix_preparer
        self.portfolio_strategy_optimizer_factory = portfolio_strategy_optimizer_factory
        self.stage_data_manager = stage_data_manager
        self.evaluator = evaluator
        self.executor = executor
        self.strategy_debug = strategy_debug

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """Process the portfolio optimization stage by aggregating all symbol data and optimizing the portfolio as a whole."""
        results = {}
        portfolio_matrix = await self._get_input_matrix(data)
        # If no valid portfolio data is available, log a warning and return empty results
        if portfolio_matrix is None:
            self.logger.warning("No valid portfolio data available for optimization.")
            return results

        self.logger.info(
            f"Starting portfolio optimization for dates {self.start_date} to {self.end_date} with {len(portfolio_matrix)} rows of data."
        )
        self.logger.debug(
            f"DEBUG: Starting _process_and_write with data keys: {list(data.keys()) if data else 'None'}"
        )
        self.logger.debug(
            f"DEBUG: Portfolio matrix shape: {portfolio_matrix.shape if portfolio_matrix is not None else 'None'}"
        )
        self.logger.debug(f"DEBUG: Portfolio matrix: {portfolio_matrix}")
        self.logger.debug(f"DEBUG: Prepared data keys: {list(data.keys())}")
        self.logger.debug(
            f"DEBUG: Portfolio matrix before optimization: {portfolio_matrix}"
        )
        self.logger.debug(
            f"DEBUG: Strategy combinators: {[combinator.__name__ for combinator in self.strategy_combinators]}"
        )

        try:
            self.logger.debug(f"DEBUG: Starting optimization process with data: {data}")
            self.logger.debug(f"DEBUG: Portfolio matrix: {portfolio_matrix}")
        except Exception as e:
            self.logger.error(f"Error during debug logging in _process_and_write: {e}")

        for strategy_combinator in self.strategy_combinators:
            self.logger.debug(
                f"DEBUG: Using strategy combinator: {strategy_combinator.__name__}"
            )
            combinations = strategy_combinator.all_strategy_combinations(
                logger=self.logger, debug=self.strategy_debug
            )
            for strat_factory in combinations:
                try:
                    strategy_class = (
                        strat_factory.func
                        if hasattr(strat_factory, "func")
                        else strat_factory
                    )
                    strategy_name = (
                        strategy_class.__name__
                        if hasattr(strategy_class, "__name__")
                        else str(strategy_class)
                    )
                    symbols = list(data.keys())
                    self.logger.debug(f"DEBUG: Optimizing strategy: {strategy_name}")
                    optimizer = self.portfolio_strategy_optimizer_factory.create(
                        strategy_class=strategy_class,
                        backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                            strat, df_
                        ),
                        metric_name=PortfolioMetric.SHARPE_RATIO,
                    )
                    optimization_result = await optimizer.optimize(
                        symbols=symbols,
                        df=portfolio_matrix,
                        window_start_time=self.start_date,
                        window_end_time=self.end_date,
                    )
                    self.logger.debug(
                        f"DEBUG: Optimization result for {strategy_name}: {optimization_result}"
                    )

                    if not self._validate_optimization_results(optimization_result):
                        self.logger.warning(
                            f"Validation failed for optimization results of {strategy_name} during {self.window_id}. Skipping."
                        )
                        continue

                    results = self._write_results(
                        start_date=self.start_date,
                        end_date=self.end_date,
                        strategy_name=strategy_name,
                        optimization_result=optimization_result,
                        collective_results=results,
                    )
                    self.logger.debug(
                        f"DEBUG: Results updated for {strategy_name}: {results}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Portfolio optimization failed for strategy {strategy_name}: {e}"
                    )
                    continue
        return results

    async def _get_input_matrix(
        self, data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]
    ) -> Optional[pd.DataFrame]:
        """Get the input matrix for the portfolio optimization."""
        try:
            if not data:
                self.logger.warning("No data provided for portfolio optimization.")
                return None
            # Aggregate all symbol data into a single DataFrame
            self.logger.info(
                f"Aggregating data for {len(data)} symbols for portfolio optimization."
            )
            self.logger.debug(
                f"DEBUG: Starting _get_input_matrix with data keys: {list(data.keys()) if data else 'None'}"
            )
            try:
                self.logger.debug(
                    f"DEBUG: Aggregating data for symbols: {list(data.keys())}"
                )
                self.logger.debug(f"DEBUG: Data provided: {data}")
            except Exception as e:
                self.logger.error(
                    f"Error during debug logging in _get_input_matrix: {e}"
                )

            all_dfs = []
            for symbol, df_iter_factory in data.items():
                self.logger.debug(f"DEBUG: Processing symbol: {symbol}")
                async for df in df_iter_factory():
                    self.logger.debug(f"DEBUG: DataFrame for {symbol}: {df}")
                    self.logger.debug(f"DEBUG: DataFrame columns: {df.columns}")
                    self.logger.debug(f"DEBUG: DataFrame shape: {df.shape}")
                    # Diagnostics for NaNs and value range
                    self.logger.debug(f"DEBUG: {symbol} head:\n{df.head()}")
                    self.logger.debug(f"DEBUG: {symbol} tail:\n{df.tail()}")
                    self.logger.debug(f"DEBUG: {symbol} NaN count:\n{df.isna().sum()}")
                    self.logger.debug(
                        f"DEBUG: {symbol} min:\n{df.min(numeric_only=True)}"
                    )
                    self.logger.debug(
                        f"DEBUG: {symbol} max:\n{df.max(numeric_only=True)}"
                    )
                    df["symbol"] = symbol  # Optionally tag symbol
                    all_dfs.append(df)

            if not all_dfs:
                self.logger.warning("No data for portfolio optimization window.")
                return None

            portfolio_df = pd.concat(all_dfs, ignore_index=True)
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame head:\n{portfolio_df.head()}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame tail:\n{portfolio_df.tail()}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame NaN count:\n{portfolio_df.isna().sum()}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame min:\n{portfolio_df.min(numeric_only=True)}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame max:\n{portfolio_df.max(numeric_only=True)}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame columns: {portfolio_df.columns}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame shape: {portfolio_df.shape}"
            )

            try:
                self.logger.debug(
                    f"DEBUG: Preparing asset-matrix for portfolio DataFrame with shape: {portfolio_df.shape}"
                )
                self.logger.debug(
                    f"DEBUG: Filtered portfolio DataFrame: {portfolio_df}"
                )
                self.logger.debug(
                    f"DEBUG: Filtered portfolio DataFrame columns: {portfolio_df.columns}"
                )
                self.logger.debug(
                    f"DEBUG: Filtered portfolio DataFrame shape: {portfolio_df.shape}"
                )
                portfolio_matrix = self.asset_matrix_preparer.prepare(
                    df=portfolio_df,
                    symbol_col=FeatureEngineeringColumns.SYMBOL,
                    timestamp_col=FeatureEngineeringColumns.TIMESTAMP,
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame head:\n{portfolio_matrix.head()}"
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame tail:\n{portfolio_matrix.tail()}"
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame NaN count:\n{portfolio_matrix.isna().sum()}"
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame min:\n{portfolio_matrix.min(numeric_only=True)}"
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame max:\n{portfolio_matrix.max(numeric_only=True)}"
                )
                self.logger.debug(
                    f"DEBUG: Asset-matrix DataFrame shape: {portfolio_matrix.shape}"
                )
                return portfolio_matrix
            except Exception as e:
                self.logger.error(
                    f"Error preparing portfolio matrix for optimization: {e}"
                )
                return None
        except Exception as e:
            self.logger.error(f"Error preparing portfolio matrix for optimization: {e}")
            return None

    def _get_output_path(self, strategy_name, start_date: datetime, end_date: datetime):
        """Get the output path for the optimization results JSON file."""
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / self.optimization_json_filename

    def _backtest_and_evaluate(self, strategy, df):
        try:
            self.logger.info(
                f"Running backtest for strategy {strategy.get_id()} on data from {df.index.min()} to {df.index.max()}"
            )
            backtest_results = self.executor.run_backtest(strategy, df)
            self.logger.debug(
                f"Backtest results for strategy {strategy.get_id()}: {backtest_results}"
            )
            metrics = self.evaluator.evaluate_from_dict(backtest_results)
            self.logger.debug(
                f"Backtest completed for strategy {strategy.get_id()} with metrics: {metrics}"
            )
            self.logger.info(
                f"Backtest completed for strategy {strategy.get_id()} with metrics: {metrics}"
            )
            # Return only the metrics dict for clarity and consistency
            return metrics
        except Exception as e:
            self.logger.error(f"Portfolio backtest/evaluation failed: {e}")
            return {}

    def _validate_optimization_results(
        self,
        results: Dict[str, Any],
    ) -> bool:
        """Validate the optimization results to ensure they contain the expected structure."""
        try:
            validation_method = (
                BacktestStage.PORTFOLIO_OPTIMIZATION.value.output_validation_fn
            )
            if not validation_method:
                self.logger.warning(
                    "No validation method defined for portfolio optimization results. Skipping validation."
                )
                return False

            # Wrap the results in the required structure for validation
            structured_results = {
                self.window_id: {
                    "optimization": results,
                    "window": {
                        "start_date": self.start_date.strftime("%Y-%m-%d"),
                        "end_date": self.end_date.strftime("%Y-%m-%d"),
                        "window_id": f"{self.start_date.strftime('%Y%m%d')}_{self.end_date.strftime('%Y%m%d')}",
                    },
                }
            }
            return validation_method(structured_results, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating optimization results: {e}. Results: {results}"
            )
            return False

    def _write_results(
        self,
        start_date: datetime,
        end_date: datetime,
        strategy_name: str,
        optimization_result: Dict[str, Any],
        collective_results: Dict[str, Dict[str, dict]],
    ) -> Dict[str, Dict[str, dict]]:
        """Write the optimization results to a JSON file (cleaned up format)."""
        try:
            optimization_json = {
                self.window_id: {
                    "optimization": optimization_result,
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
                start_date=start_date,
                end_date=end_date,
            )
            if existing_optimization_json is None:
                self.logger.warning(
                    f"No existing optimization results for {strategy_name} {self.window_id}"
                )
                existing_optimization_json = {}

            updated_optimization_json = self._deep_merge(
                existing_optimization_json, optimization_json
            )
            # Save optimization metrics to optimization_result.json under window_id
            out_path = self._get_output_path(
                strategy_name,
                start_date,
                end_date,
            )
            self.logger.info(
                f"Saving portfolio optimization summary for PORTFOLIO {strategy_name} to {out_path}"
            )
            with open(out_path, "w") as f:
                json.dump(updated_optimization_json, f, indent=2, default=str)

            # Update the results dictionary to match the validator's requirements
            collective_results[strategy_name] = updated_optimization_json
        except Exception as e:
            self.logger.error(
                f"Error writing optimization results for {strategy_name} during {self.window_id}: {e}"
            )
        return collective_results

    def get_existing_optimization_results(
        self, strategy_name: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, dict]:
        """Retrieve existing optimization results for a given strategy and symbol."""
        try:
            self.logger.info(
                f"Retrieving optimization results for {strategy_name} during {self.window_id}"
            )
            train_opt_results = self._get_optimization_results(
                strategy_name=strategy_name,
                symbol=None,
                start_date=start_date,
                end_date=end_date,
            )
            if train_opt_results is None:
                self.logger.warning(
                    f"No optimization result for {strategy_name} {self.window_id}"
                )
                return {}
            return train_opt_results
        except Exception as e:
            self.logger.error(
                f"Error retrieving optimization results for {strategy_name} during {self.window_id}: {e}"
            )
            return None
