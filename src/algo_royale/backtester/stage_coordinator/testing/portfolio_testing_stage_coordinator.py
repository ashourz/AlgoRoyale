import inspect
import json
from logging import Logger
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
from algo_royale.backtester.stage_coordinator.testing.base_testing_stage_coordinator import (
    BaseTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class PortfolioTestingStageCoordinator(BaseTestingStageCoordinator):
    """Coordinator for the portfolio testing stage of the backtest pipeline.
    This class is responsible for testing portfolio strategies using the provided data loader,
    and executor. It handles the evaluation of backtest results and manages
    optimization results for portfolio strategies.
    Parameters:
        data_loader (SymbolStrategyDataLoader): Loader for stage data.
        stage_data_manager (StageDataManager): Manager for stage data directories.
        logger (Logger): Logger for logging information and errors.
        strategy_combinators (Sequence[type[PortfolioStrategyCombinator]]): List of strategy combinators.
        executor (PortfolioBacktestExecutor): Executor for running portfolio backtests.
        evaluator (PortfolioBacktestEvaluator): Evaluator for assessing portfolio backtest results.
        optimization_root (str): Root directory for saving optimization results.
        optimization_json_filename (str): Name of the JSON file to save optimization results.
        asset_matrix_preparer (AssetMatrixPreparer): Preparer for converting data to asset-matrix form.
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
    ):
        super().__init__(
            stage=BacktestStage.PORTFOLIO_TESTING,
            data_loader=data_loader,
            stage_data_manager=stage_data_manager,
            logger=logger,
            evaluator=evaluator,
            executor=executor,
            strategy_combinators=strategy_combinators,
            optimization_json_filename=optimization_json_filename,
            optimization_root=optimization_root,
        )

        self.asset_matrix_preparer = asset_matrix_preparer

    async def _process_and_write(
        self,
        data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        The injected executor should be pre-configured with initial_balance, transaction_cost, min_lot, leverage, and slippage.
        This method does not set these parameters per run.
        """
        results = {}
        portfolio_matrix = await self._get_input_matrix(data)
        # If no valid portfolio data is available, log a warning and return empty results
        if portfolio_matrix is None:
            self.logger.warning("No valid portfolio data available for optimization.")
            return results

        # TODO: Validate portfolio_matrix structure

        self.logger.info(
            f"Starting portfolio testing for window {self.test_window_id} with {len(portfolio_matrix)} rows of data."
        )
        for strategy_combinator in self.strategy_combinators:
            for strat_factory in strategy_combinator.all_strategy_combinations():
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
                # Retrieve optimized parameters for the strategy
                optimize_params = self._get_optimized_params(
                    strategy_name=strategy_name,
                    strategy_class=strategy_class,
                )
                if not optimize_params:
                    self.logger.warning(
                        f"No optimized parameters found for {strategy_name} during {self.train_window_id}. Skipping."
                    )
                    continue
                # Instantiate strategy with filtered_params
                strategy = strategy_class(**optimize_params)
                # Run backtest using the pre-configured executor
                backtest_results = self.executor.run_backtest(
                    strategy,
                    portfolio_matrix,
                )
                self.logger.info(
                    f"Backtest completed for {strategy_name} with {len(backtest_results.get('portfolio_returns', []))} returns."
                )
                # Evaluate metrics (now includes all new metrics)
                metrics = self.evaluator.evaluate(strategy, backtest_results)
                test_opt_results = self._get_optimization_results(
                    strategy_name=strategy_name,
                    symbol=None,
                    start_date=self.test_start_date,
                    end_date=self.test_end_date,
                )
                # Validate optimization results
                if not self._validate_optimization_results(test_opt_results):
                    self.logger.warning(
                        f"Validation failed for optimization results of {strategy_name} during {self.test_window_id}. Skipping writing results."
                    )
                    continue

                results = self._write_test_results(
                    symbols=list(data.keys()),
                    metrics=metrics,
                    strategy_name=strategy_name,
                    backtest_results=backtest_results,
                    optimization_result=test_opt_results,
                    results=results,
                )

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
            all_dfs = []
            for symbol, df_iter_factory in data.items():
                async for df in df_iter_factory():
                    ## TODO: VALIDATE DATAFRAME
                    df["symbol"] = symbol  # Optionally tag symbol
                    all_dfs.append(df)
            if not all_dfs:
                self.logger.warning("No data for portfolio optimization window.")
                return {}

            portfolio_df = pd.concat(all_dfs, ignore_index=True)
            self.logger.debug(
                f"Combined portfolio DataFrame shape: {portfolio_df.shape}, columns: {list(portfolio_df.columns)}"
            )
            self.logger.debug(
                f"Combined portfolio DataFrame index: {portfolio_df.index}"
            )
            # Prepare asset-matrix form for portfolio strategies
            portfolio_matrix = self.asset_matrix_preparer.prepare(portfolio_df)
            self.logger.info(
                f"Asset-matrix DataFrame shape: {portfolio_matrix.shape}, columns: {portfolio_matrix.columns}"
            )
            return portfolio_matrix
        except Exception as e:
            self.logger.error(f"Error preparing portfolio matrix for optimization: {e}")
            return None

    def _get_optimized_params(
        self,
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
                symbol=None,
                start_date=self.train_start_date,
                end_date=self.train_end_date,
            )
            if not train_opt_results:
                print(
                    f"No optimization results found for PORTFOLIO {strategy_name} {self.train_window_id}"
                )
                self.logger.warning(
                    f"No optimization result for PORTFOLIO {strategy_name} {self.train_window_id}"
                )
                return None
            # Validate the optimization results structure
            if not self._validate_optimization_results(train_opt_results):
                self.logger.warning(
                    f"Validation failed for optimization results of {strategy_name} during {self.train_window_id}. Skipping."
                )
                return None
            if (
                self.train_window_id not in train_opt_results
                or "optimization" not in train_opt_results[self.train_window_id]
            ):
                print(
                    f"No optimization results found for PORTFOLIO {strategy_name} {self.train_window_id}"
                )
                self.logger.warning(
                    f"No optimization result for PORTFOLIO {strategy_name} {self.train_window_id}"
                )
                return None

            best_params = train_opt_results[self.train_window_id]["optimization"][
                "best_params"
            ]
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
        validation_method = BacktestStage.PORTFOLIO_TESTING.value.input_validation_fn
        if not validation_method:
            self.logger.warning(
                "No validation method defined for portfolio optimization results. Skipping validation."
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
                "No validation method defined for portfolio test results. Skipping validation."
            )
            return False
        return validation_method(results)

    def _write_test_results(
        self,
        symbols: Sequence[str],
        metrics: Dict[str, float],
        strategy_name: str,
        backtest_results: Dict[str, Any],
        optimization_result: Dict[str, Any],
        results: Dict[str, Dict[str, Dict[str, float]]],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        try:
            if self.test_window_id not in optimization_result:
                optimization_result[self.test_window_id] = {}
            optimization_result[self.test_window_id]["test"] = {
                "metrics": metrics,
                "transactions": backtest_results.get("transactions", []),
            }
            # Save optimization metrics to optimization_result.json under window_id
            out_path = self._get_optimization_result_path(
                strategy_name=strategy_name,
                start_date=self.test_start_date,
                end_date=self.test_end_date,
            )
            with open(out_path, "w") as f:
                json.dump(optimization_result, f, indent=2, default=str)
            # Fix: results should be keyed by symbol, not 'PORTFOLIO'
            for symbol in symbols:
                results.setdefault(symbol, {}).setdefault(strategy_name, {})[
                    self.test_window_id
                ] = metrics
        except Exception as e:
            self.logger.error(
                f"Error writing test results for {strategy_name} during {self.test_window_id}: {e}"
            )
        return results
