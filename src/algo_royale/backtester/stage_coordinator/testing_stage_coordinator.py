import json
from datetime import datetime
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.base_backtest_evaluator import BacktestEvaluator
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.strategy_factory import StrategyFactory


class TestingStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_factory: StrategyFactory,
        logger: Logger,
        strategy_combinators: Optional[Sequence[type[StrategyCombinator]]] = None,
    ):
        """Coordinator for the backtest stage.
        Args:
            config: Configuration object.
            data_loader: Data loader for the stage.
            data_preparer: Data preparer for the stage.
            data_writer: Data writer for the stage.
            stage_data_manager: Stage data manager.
            logger: Logger instance.
            strategy_combinators: List of strategy combinator classes to use.
        """
        super().__init__(
            stage=BacktestStage.BACKTEST,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_combinators = strategy_combinators
        if not self.strategy_combinators:
            raise ValueError("No strategy combinators provided")
        self.executor = strategy_executor
        self.evaluator = strategy_evaluator
        self.strategy_factory = strategy_factory
        self.strategy_names = [
            combinator.strategy_class.__name__
            for combinator in self.strategy_combinators
        ]

    async def run(
        self,
        train_start_date: datetime,
        train_end_date: datetime,
        test_start_date: datetime,
        test_end_date: datetime,
    ) -> bool:
        """Run the backtest stage."""
        self.train_start_date = train_start_date
        self.train_end_date = train_end_date
        self.train_window_id = (
            f"{train_start_date.strftime('%Y%m%d')}_{train_end_date.strftime('%Y%m%d')}"
        )
        return super().run(start_date=test_start_date, end_date=test_end_date)

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Run backtests for all strategies in the watchlist using the best parameters from optimization."""
        results = {}

        for symbol, df_iter_factory in prepared_data.items():
            if symbol not in prepared_data:
                self.logger.warning(f"No prepared data for symbol: {symbol}")
                continue

            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window {self.train_window_id}"
                )
                continue
            test_df = pd.concat(dfs, ignore_index=True)

            for strategy_name in self.strategy_names:
                # Load best params from optimization_result.json
                out_dir = self.stage_data_manager.get_directory_path(
                    BacktestStage.OPTIMIZATION, strategy_name, symbol
                )
                out_path = out_dir / "optimization_result.json"
                if not out_path.exists():
                    self.logger.warning(
                        f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue
                with open(out_path, "r") as f:
                    opt_results = json.load(f)
                if (
                    self.train_window_id not in opt_results
                    or "optimization" not in opt_results[self.train_window_id]
                ):
                    self.logger.warning(
                        f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                    )
                    continue
                best_params = opt_results[self.train_window_id]["optimization"][
                    "best_params"
                ]

                # Instantiate strategy and run backtest
                strategy = self.strategy_factory.build_strategy(
                    strategy_name, best_params
                )

                async def data_factory():
                    yield test_df

                raw_results = await self.executor.run_backtest(
                    [strategy], {symbol: data_factory}
                )
                dfs = raw_results.get(symbol, [])
                if not dfs:
                    self.logger.warning(
                        f"No test results for {symbol} {strategy_name} {self.window_id}"
                    )
                    continue
                full_df = pd.concat(dfs, ignore_index=True)
                metrics = self.evaluator.evaluate(strategy, full_df)

                # Save test metrics to optimization_result.json under window_id
                if self.window_id not in opt_results:
                    opt_results[self.window_id] = {}
                opt_results[self.window_id]["test"] = {
                    "metrics": metrics,
                    "window": {
                        "start_date": self.start_date.strftime("%Y-%m-%d"),
                        "end_date": self.end_date.strftime("%Y-%m-%d"),
                    },
                }
                with open(out_path, "w") as f:
                    json.dump(opt_results, f, indent=2, default=str)

                results.setdefault(symbol, {})[strategy_name] = {
                    self.window_id: metrics
                }

        return results

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
