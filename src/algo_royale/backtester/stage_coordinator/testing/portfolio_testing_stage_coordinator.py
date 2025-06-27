import inspect
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
from algo_royale.backtester.stage_coordinator.testing.base_testing_stage_coordinator import (
    BaseTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.utils.asset_matrix_preparer import AssetMatrixPreparer


##TODO: THIS IS NOT REALLY NEEDED
class PortfolioTestingStageCoordinator(BaseTestingStageCoordinator):
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
            stage=BacktestStage.PORTFOLIO_TESTING,
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
        self.asset_matrix_preparer = asset_matrix_preparer

    async def run(
        self,
        train_start_date: datetime,
        train_end_date: datetime,
        test_start_date: datetime,
        test_end_date: datetime,
    ) -> bool:
        self.train_start_date = train_start_date
        self.train_end_date = train_end_date
        self.train_window_id = (
            f"{train_start_date.strftime('%Y%m%d')}_{train_end_date.strftime('%Y%m%d')}"
        )
        self.logger.info(
            f"Running portfolio backtest for window {self.train_window_id} from {train_start_date} to {train_end_date}"
        )
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.test_window_id = (
            f"{test_start_date.strftime('%Y%m%d')}_{test_end_date.strftime('%Y%m%d')}"
        )
        self.logger.info(
            f"Running portfolio backtest for test window {self.test_window_id} from {test_start_date} to {test_end_date}"
        )
        return await super().run(start_date=test_start_date, end_date=test_end_date)

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        The injected executor should be pre-configured with initial_balance, transaction_cost, min_lot, leverage, and slippage.
        This method does not set these parameters per run.
        """
        results = {}
        all_dfs = []
        for symbol, df_iter_factory in prepared_data.items():
            async for df in df_iter_factory():
                df["symbol"] = symbol  # Optionally tag symbol
                all_dfs.append(df)
        if not all_dfs:
            self.logger.warning("No data for portfolio testing window.")
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
                train_opt_results = self.get_optimization_results(
                    strategy_name,
                    self.train_start_date,
                    self.train_end_date,
                )
                if not train_opt_results:
                    self.logger.warning(
                        f"No optimization result for PORTFOLIO {strategy_name} {self.train_window_id}"
                    )
                    continue
                if (
                    self.train_window_id not in train_opt_results
                    or "optimization" not in train_opt_results[self.train_window_id]
                ):
                    self.logger.warning(
                        f"No optimization result for PORTFOLIO {strategy_name} {self.train_window_id}"
                    )
                    continue
                best_params = train_opt_results[self.train_window_id]["optimization"][
                    "best_params"
                ]
                valid_params = set(
                    inspect.signature(strategy_class.__init__).parameters
                )
                filtered_params = {
                    k: v
                    for k, v in best_params.items()
                    if k in valid_params and k != "self"
                }
                self.logger.info(f"Filtered params: {filtered_params}")
                # Instantiate strategy with filtered_params
                strategy = strategy_class(**filtered_params)
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
                test_opt_results = self.get_optimization_results(
                    strategy_name, self.test_start_date, self.test_end_date
                )
                if self.test_window_id not in test_opt_results:
                    test_opt_results[self.test_window_id] = {}
                test_opt_results[self.test_window_id]["test"] = {
                    "metrics": metrics,
                    "transactions": backtest_results.get("transactions", []),
                }
                # Save optimization metrics to optimization_result.json under window_id
                out_path = self.get_output_path(
                    strategy_name, self.test_start_date, self.test_end_date
                )
                with open(out_path, "w") as f:
                    json.dump(test_opt_results, f, indent=2, default=str)
                results.setdefault("PORTFOLIO", {})[strategy_name] = {
                    self.test_window_id: metrics
                }
        return results

    def get_optimization_results(
        self, strategy_name: str, start_date: datetime, end_date: datetime
    ) -> Dict:
        json_path = self.get_output_path(strategy_name, start_date, end_date)
        self.logger.debug(
            f"Loading optimization results from {json_path} for {strategy_name}"
        )
        if not json_path.exists() or json_path.stat().st_size == 0:
            self.logger.warning(
                f"No optimization result for {strategy_name} start_date={start_date}, end_date={end_date} (optimization result file does not exist or is empty)"
            )
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w") as f:
                json.dump({}, f)
            return {}
        with open(json_path, "r") as f:
            try:
                opt_results = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Optimization result file {json_path} is not valid JSON. Returning empty dict."
                )
                return {}
        return opt_results

    def get_output_path(
        self, strategy_name: str, start_date: datetime, end_date: datetime
    ):
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

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
