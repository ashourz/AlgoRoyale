import inspect
import json
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

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
from algo_royale.backtester.stage_coordinator.testing.base_testing_stage_coordinator import (
    BaseTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.writer.stage_data_writer import StageDataWriter
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class PortfolioTestingStageCoordinator(BaseTestingStageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: StageDataPreparer,
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
            optimization_json_filename=optimization_json_filename,
            optimization_root=optimization_root,
        )

        self.asset_matrix_preparer = asset_matrix_preparer

    async def _process(
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
                    continue
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
                test_opt_results = self._get_optimization_results(
                    strategy_name=strategy_name,
                    symbol=None,
                    start_date=self.test_start_date,
                    end_date=self.test_end_date,
                )
                if self.test_window_id not in test_opt_results:
                    test_opt_results[self.test_window_id] = {}
                test_opt_results[self.test_window_id]["test"] = {
                    "metrics": metrics,
                    "transactions": backtest_results.get("transactions", []),
                }
                # Save optimization metrics to optimization_result.json under window_id
                out_path = self._get_optimization_result_path(
                    strategy_name=strategy_name,
                    symbol=None,
                    start_date=self.test_start_date,
                    end_date=self.test_end_date,
                )
                with open(out_path, "w") as f:
                    json.dump(test_opt_results, f, indent=2, default=str)
                # Fix: results should be keyed by symbol, not 'PORTFOLIO'
                for symbol in prepared_data.keys():
                    results.setdefault(symbol, {}).setdefault(strategy_name, {})[
                        self.test_window_id
                    ] = metrics
        return results

    def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[str, Dict[str, Dict[str, float]]],
    ) -> None:
        """
        No-op: writing is handled in process().
        """
        self.logger.info(f"Processed data for stage {stage} is ready, but not written.")
        # Writing is handled in _process() where optimization results are saved
