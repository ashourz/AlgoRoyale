import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.stage_coordinator.optimization.base_optimization_stage_coordinator import (
    BaseOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.optimizer.portfolio_strategy_optimizer import (
    PortfolioStrategyOptimizer,
)
from algo_royale.portfolio.utils.asset_matrix_preparer import AssetMatrixPreparer


class PortfolioOptimizationStageCoordinator(BaseOptimizationStageCoordinator):
    """
    Coordinator for the portfolio optimization stage of the backtest pipeline.
    Optimizes portfolio strategies for a list of symbols using the provided data loader, data preparer, data writer, and optimizer.
    """

    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
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
            stage=BacktestStage.PORTFOLIO_OPTIMIZATION,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
            evaluator=evaluator,
            executor=executor,
            strategy_combinators=strategy_combinators,
        )
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.optimization_json_filename = optimization_json_filename
        self.asset_matrix_preparer = asset_matrix_preparer  # NEW

    async def process(
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
            f"Starting portfolio optimization for window {self.window_id} with {len(portfolio_matrix)} rows of data."
        )
        for strategy_combinator in self.strategy_combinators:
            for strat_factory in strategy_combinator.all_strategy_combinations(
                logger=self.logger
            ):
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
                try:
                    optimizer = PortfolioStrategyOptimizer(
                        strategy_class=strategy_class,
                        backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                            strat, df_
                        ),
                        logger=self.logger,
                    )
                    optimization_result = await optimizer.optimize(
                        "PORTFOLIO", portfolio_matrix
                    )
                except Exception as e:
                    self.logger.error(
                        f"Portfolio optimization failed for strategy {strategy_name}: {e}"
                    )
                    continue
                # Save optimization metrics to optimization_result.json under window_id
                out_path = self.get_output_path(
                    strategy_name,
                    self.start_date,
                    self.end_date,
                )
                self.logger.info(
                    f"Saving portfolio optimization results for PORTFOLIO {strategy_name} to {out_path}"
                )
                if out_path.exists():
                    with open(out_path, "r") as f:
                        opt_results = json.load(f)
                else:
                    opt_results = {}
                if self.window_id not in opt_results:
                    opt_results[self.window_id] = {}
                opt_results[self.window_id]["optimization"] = optimization_result
                opt_results[self.window_id]["window"] = {
                    "start_date": str(self.start_date),
                    "end_date": str(self.end_date),
                }
                with open(out_path, "w") as f:
                    json.dump(opt_results, f, indent=2, default=str)
                results.setdefault("PORTFOLIO", {})[strategy_name] = {
                    self.window_id: optimization_result
                }
        return results

    def get_output_path(self, strategy_name, start_date: datetime, end_date: datetime):
        """Get the output path for the optimization results JSON file."""
        out_dir = self.stage_data_manager.get_extended_path(
            base_dir=self.optimization_root,
            strategy_name=strategy_name,
            symbol=None,
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
            metrics = self.evaluator.evaluate(strategy, backtest_results)
            return {"metrics": metrics}
        except Exception as e:
            self.logger.error(f"Portfolio backtest/evaluation failed: {e}")
            return {"metrics": {}}

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
