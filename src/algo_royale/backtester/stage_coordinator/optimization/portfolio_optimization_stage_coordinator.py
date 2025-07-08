import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

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
        logger: Logger,
        strategy_combinators: Sequence[type[PortfolioStrategyCombinator]],
        executor: PortfolioBacktestExecutor,
        evaluator: PortfolioBacktestEvaluator,
        optimization_root: str,
        optimization_json_filename: str,
        asset_matrix_preparer: AssetMatrixPreparer,
        portfolio_strategy_optimizer_factory: PortfolioStrategyOptimizerFactory,
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

        # TODO: Validate portfolio_matrix structure

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

        print(f"DEBUG: Prepared data keys: {list(data.keys())}")
        print(f"DEBUG: Portfolio matrix before optimization: {portfolio_matrix}")
        print(
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
                logger=self.logger
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
                    self.logger.debug(f"DEBUG: Optimizing strategy: {strategy_name}")
                    optimizer = self.portfolio_strategy_optimizer_factory.create(
                        strategy_class=strategy_class,
                        backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                            strat, df_
                        ),
                        metric_name=PortfolioMetric.SHARPE_RATIO,
                    )
                    optimization_result = await optimizer.optimize(
                        self.stage.name, portfolio_matrix
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
                        symbols=list(data.keys()),
                        start_date=self.start_date,
                        end_date=self.end_date,
                        strategy_name=strategy_name,
                        optimization_result=optimization_result,
                        results=results,
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
                    df["symbol"] = symbol  # Optionally tag symbol
                    all_dfs.append(df)

            if not all_dfs:
                self.logger.warning("No data for portfolio optimization window.")
                return None

            portfolio_df = pd.concat(all_dfs, ignore_index=True)
            self.logger.debug(f"DEBUG: Combined portfolio DataFrame: {portfolio_df}")
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame columns: {portfolio_df.columns}"
            )
            self.logger.debug(
                f"DEBUG: Combined portfolio DataFrame shape: {portfolio_df.shape}"
            )

            try:
                print(f"DEBUG: Combined portfolio DataFrame: {portfolio_df}")
                print(
                    f"DEBUG: Combined portfolio DataFrame columns: {portfolio_df.columns}"
                )
                print(
                    f"DEBUG: Combined portfolio DataFrame shape: {portfolio_df.shape}"
                )
                portfolio_matrix = self.asset_matrix_preparer.prepare(portfolio_df)
                print(f"DEBUG: Asset-matrix DataFrame shape: {portfolio_matrix.shape}")
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
            print(f"DEBUG: run_backtest returned: {backtest_results}")
            metrics = self.evaluator.evaluate(strategy, backtest_results)
            print(f"DEBUG: evaluator.evaluate returned: {metrics}")
            self.logger.info(
                f"Backtest completed for strategy {strategy.get_id()} with metrics: {metrics}"
            )
            print(f"DEBUG: _backtest_and_evaluate returns metrics: {metrics}")
            # Return only the metrics dict for clarity and consistency
            return metrics
        except Exception as e:
            self.logger.error(f"Portfolio backtest/evaluation failed: {e}")
            print(f"DEBUG: _backtest_and_evaluate exception: {e}")
            return {}

    def _validate_optimization_results(
        self,
        results: Dict[str, Any],
    ) -> bool:
        """Validate the optimization results to ensure they contain the expected structure."""
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
                "window": {"start_date": self.start_date, "end_date": self.end_date},
            }
        }
        return validation_method(structured_results)

    def _write_results(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        strategy_name: str,
        optimization_result: Dict[str, Any],
        results: Dict[str, Dict[str, dict]],
    ) -> Dict[str, Dict[str, dict]]:
        """Write the optimization results to a JSON file.
        This method saves the optimization results for the given strategy and symbols
        to the optimization_result.json file under the specified window_id.
        It ensures that the results are stored in a structured format, keyed by symbol and strategy name
        """
        try:
            # Update the results dictionary with the optimization results
            for symbol in symbols:
                results.setdefault(symbol, {}).setdefault(strategy_name, {}).setdefault(
                    self.window_id, {}
                )
                results[symbol][strategy_name][self.window_id] = {
                    "optimization": optimization_result,
                    "window": {
                        "start_date": str(start_date),
                        "end_date": str(end_date),
                    },
                }

            # Save optimization metrics to optimization_result.json under window_id
            out_path = self._get_output_path(
                strategy_name,
                start_date,
                end_date,
            )
            self.logger.info(
                f"Saving portfolio optimization results for PORTFOLIO {strategy_name} to {out_path}"
            )
            # Write the updated results back to the file
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(
                f"Error writing optimization results for {strategy_name} during {self.window_id}: {e}"
            )
        return results
