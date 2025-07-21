import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

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
from algo_royale.backtester.stage_data.loader.portfolio_matrix_loader import (
    PortfolioMatrixLoader,
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
        portfolio_strategy_optimizer_factory (PortfolioStrategyOptimizerFactory): Factory to create portfolio strategy optimizers.
        strategy_debug (bool): Whether to enable debug mode for strategy combinators.
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
        portfolio_matrix_loader: PortfolioMatrixLoader,
        portfolio_strategy_optimizer_factory: PortfolioStrategyOptimizerFactory,
        strategy_debug: bool = False,
        optimization_n_trials: int = 1,
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
        self.portfolio_matrix_loader = portfolio_matrix_loader
        self.portfolio_strategy_optimizer_factory = portfolio_strategy_optimizer_factory
        self.stage_data_manager = stage_data_manager
        self.evaluator = evaluator
        self.executor = executor
        self.strategy_debug = strategy_debug
        self.optimization_n_trials = optimization_n_trials
        self.strategy_combinators = strategy_combinators

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """
        Process the portfolio optimization stage by aggregating all symbol data and optimizing the portfolio as a whole.

        Args:
            data (Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]):
                Optional mapping of symbol to async data loader.

        Returns:
            Dict[str, Dict[str, dict]]: Results of the optimization for each strategy.

        Note:
            The optimization is run for all symbols at once (portfolio-level optimization), not per-symbol.
        """
        try:
            results = {}
            portfolio_matrix = await self._get_portfolio_matrix()
            if portfolio_matrix is None or portfolio_matrix.empty:
                self.logger.warning(
                    "No valid portfolio data available for optimization. Skipping stage."
                )
                return results

            # If no valid portfolio data is available, log a warning and return empty results
            if portfolio_matrix is None:
                self.logger.warning(
                    "No valid portfolio data available for optimization."
                )
                return results

            self.logger.info(
                f"Starting portfolio optimization: {len(portfolio_matrix)} rows, {self.start_date} to {self.end_date}."
            )
            self.logger.debug(
                f"Portfolio matrix shape: {portfolio_matrix.shape}, columns: {list(portfolio_matrix.columns)}"
            )
            self.logger.debug(
                f"Strategy combinators: {[c.__name__ for c in self.strategy_combinators]}"
            )
            self.logger.debug(f"Data keys: {list(data.keys()) if data else 'None'}")

            for strategy_combinator in self.strategy_combinators:
                self.logger.info(
                    f"Using strategy combinator: {strategy_combinator.__name__}"
                )
                combinations = strategy_combinator.all_strategy_combinations(
                    logger=self.logger,
                    debug=self.strategy_debug,
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
                        self.logger.info(
                            f"Optimizing symbols: {symbols} strategy: {strategy_name} for window {self.window_id}"
                        )
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
                            n_trials=self.optimization_n_trials,
                        )
                        self.logger.info(
                            f"Optimization result for {strategy_name} ({self.window_id}) written."
                        )

                        if not self._validate_optimization_results(optimization_result):
                            self.logger.warning(
                                f"Validation failed for {strategy_name} ({self.window_id}). Skipping."
                            )
                            continue

                        results = self._write_results(
                            start_date=self.start_date,
                            end_date=self.end_date,
                            strategy_name=strategy_name,
                            optimization_result=optimization_result,
                            collective_results=results,
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Portfolio optimization failed for {strategy_name} ({self.window_id}): {e}"
                        )
                        continue
            return results
        except Exception as e:
            self.logger.error(
                f"Error during portfolio optimization stage processing: {e}"
            )
            return {}

    async def _get_portfolio_matrix(
        self,
    ) -> Optional[pd.DataFrame]:
        """
        Load the portfolio matrix for the optimization stage.

        Returns:
            Optional[pd.DataFrame]: The portfolio matrix DataFrame, or None if not available.
        """
        try:
            watchlist = self.data_loader.get_watchlist()
            if not watchlist:
                self.logger.error("Watchlist is empty. Cannot load portfolio matrix.")
                return None
            portfolio_matrix = await self.portfolio_matrix_loader.get_portfolio_matrix(
                symbols=watchlist,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            if portfolio_matrix is None or portfolio_matrix.empty:
                self.logger.warning(
                    "No valid portfolio data available for optimization."
                )
                return None
            return portfolio_matrix
        except Exception as e:
            self.logger.error(f"Error loading portfolio matrix: {e}")
            return None

    def _get_output_path(self, strategy_name, start_date: datetime, end_date: datetime):
        """
        Get the output path for the optimization results JSON file.

        Args:
            strategy_name (str): Name of the strategy.
            start_date (datetime): Start date of the window.
            end_date (datetime): End date of the window.

        Returns:
            Path: Path to the output JSON file.
        """
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / self.optimization_json_filename

    def _backtest_and_evaluate(self, strategy, df):
        """
        Run a backtest and evaluate metrics for a given portfolio strategy and DataFrame.

        Args:
            strategy: The portfolio strategy instance.
            df (pd.DataFrame): The portfolio matrix DataFrame (all symbols).

        Returns:
            dict: Metrics dictionary from the evaluation.
        """
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
        """
        Validate the optimization results to ensure they contain the expected structure.

        Args:
            results (Dict[str, Any]): The optimization results to validate.

        Returns:
            bool: True if results are valid, False otherwise.
        """
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
        """
        Write the optimization results to a JSON file (cleaned up format).

        Args:
            start_date (datetime): Start date of the window.
            end_date (datetime): End date of the window.
            strategy_name (str): Name of the strategy.
            optimization_result (Dict[str, Any]): Optimization result dictionary.
            collective_results (Dict[str, Dict[str, dict]]): Results dictionary to update.

        Returns:
            Dict[str, Dict[str, dict]]: Updated results dictionary.
        """
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
        """
        Retrieve existing optimization results for a given strategy and symbol.

        Args:
            strategy_name (str): Name of the strategy.
            start_date (datetime): Start date of the window.
            end_date (datetime): End date of the window.

        Returns:
            Dict[str, dict]: Existing optimization results dictionary.
        """
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
