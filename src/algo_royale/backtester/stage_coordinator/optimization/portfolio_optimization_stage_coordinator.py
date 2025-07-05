import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
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
        data_preparer (StageDataPreparer): Prepares data asynchronously for the stage.
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
        data_preparer: StageDataPreparer,
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
            data_preparer=data_preparer,
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
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """Process the portfolio optimization stage by aggregating all symbol data and optimizing the portfolio as a whole."""
        results = {}
        all_dfs = []
        for symbol, df_iter_factory in prepared_data.items():
            async for df in df_iter_factory():
                df["symbol"] = symbol  # Optionally tag symbol
                all_dfs.append(df)
        if not all_dfs:
            self.logger.warning("No data for portfolio optimization window.")
            return {}

        portfolio_df = pd.concat(all_dfs, ignore_index=True)
        self.logger.debug(
            f"Combined portfolio DataFrame shape: {portfolio_df.shape}, columns: {list(portfolio_df.columns)}"
        )
        self.logger.debug(f"Combined portfolio DataFrame index: {portfolio_df.index}")
        # Prepare asset-matrix form for portfolio strategies
        portfolio_matrix = self.asset_matrix_preparer.prepare(portfolio_df)
        self.logger.info(
            f"Asset-matrix DataFrame shape: {portfolio_matrix.shape}, columns: {portfolio_matrix.columns}"
        )
        self.logger.info(
            f"Starting portfolio optimization for dates {self.start_date} to {self.end_date} with {len(portfolio_matrix)} rows of data."
        )
        for strategy_combinator in self.strategy_combinators:
            # All combinators must accept 'logger' as a parameter
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
                    # Save optimization metrics to optimization_result.json under window_id
                    results = self._write_results(
                        symbols=list(prepared_data.keys()),
                        start_date=self.start_date,
                        end_date=self.end_date,
                        strategy_name=strategy_name,
                        optimization_result=optimization_result,
                        results=results,
                    )
                except Exception as e:
                    self.logger.error(
                        f"Portfolio optimization failed for strategy {strategy_name}: {e}"
                    )
                    continue
        return results

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
            # Save optimization metrics to optimization_result.json under window_id
            out_path = self._get_output_path(
                strategy_name,
                start_date,
                end_date,
            )
            self.logger.info(
                f"Saving portfolio optimization results for PORTFOLIO {strategy_name} to {out_path}"
            )
            # Robust check for file existence and size (test/production compatible)
            if out_path.exists() and out_path.stat().st_size > 0:
                with open(out_path, "r") as f:
                    opt_results = json.load(f)
            else:
                opt_results = {}

            # Initialize the window_id entry if it does not exist
            # This allows us to store multiple optimizations under the same window_id
            if self.window_id not in opt_results:
                opt_results[self.window_id] = {}
            opt_results[self.window_id]["optimization"] = optimization_result
            opt_results[self.window_id]["window"] = {
                "start_date": str(start_date),
                "end_date": str(end_date),
            }
            # Write the updated results back to the file
            with open(out_path, "w") as f:
                json.dump(opt_results, f, indent=2, default=str)

            for symbol in symbols:
                results.setdefault(symbol, {}).setdefault(strategy_name, {})[
                    self.window_id
                ] = optimization_result
        except Exception as e:
            self.logger.error(
                f"Error writing optimization results for {strategy_name} during {self.window_id}: {e}"
            )
        return results
