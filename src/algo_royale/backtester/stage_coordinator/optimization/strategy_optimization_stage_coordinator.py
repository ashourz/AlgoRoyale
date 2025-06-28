import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.optimizer.signal.strategy_optimizer import StrategyOptimizer
from algo_royale.backtester.stage_coordinator.optimization.base_optimization_stage_coordinator import (
    BaseOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.strategies.base_signal_strategy import (
    BaseSignalStrategy,
)


class StrategyOptimizationStageCoordinator(BaseOptimizationStageCoordinator):
    """Coordinator for the optimization stage of the backtest pipeline.
    This class is responsible for optimizing and backtesting strategies
    for a list of symbols using the provided data loader, data preparer,
    data writer, and strategy executor.
    It also handles the evaluation of the backtest results.

    Parameters:
        data_loader: Data loader for the stage.
        data_preparer: Data preparer for the stage.
        data_writer: Data writer for the stage.
        stage_data_manager: Stage data manager.
        strategy_factory: StrategyFactory instance for creating strategies.
        logger: Logger instance.
        strategy_executor: StrategyBacktestExecutor instance for executing backtests.
        strategy_evaluator: BacktestEvaluator instance for evaluating backtest results.
        strategy_combinators: List of strategy combinator classes to use.
    """

    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_executor: StrategyBacktestExecutor,
        strategy_evaluator: BacktestEvaluator,
        strategy_combinators: Sequence[type[SignalStrategyCombinator]],
        optimization_root: str,
        optimization_json_filename: str,
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
            stage=BacktestStage.STRATEGY_OPTIMIZATION,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            executor=strategy_executor,
            evaluator=strategy_evaluator,
            strategy_combinators=strategy_combinators,
            logger=logger,
        )
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.optimization_json_filename = optimization_json_filename

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, dict]]:
        """Process the optimization stage."""
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
                    f"No data for symbol: {symbol} in window {self.window_id}"
                )
                continue
            train_df = pd.concat(dfs, ignore_index=True)

            for strategy_combinator in self.strategy_combinators:
                strategy_class = strategy_combinator.strategy_class
                strategy_name = strategy_class.__name__
                # Run optimization
                try:
                    optimizer = StrategyOptimizer(
                        strategy_class=strategy_class,
                        condition_types=strategy_combinator.get_condition_types(),
                        backtest_fn=lambda strat, df_: self._backtest_and_evaluate(
                            symbol, strat, df_
                        ),
                        logger=self.logger,
                    )
                    optimization_result = optimizer.optimize(symbol, train_df)

                except Exception as e:
                    self.logger.error(
                        f"Optimization failed for symbol {symbol}, strategy {strategy_name}: {e}"
                    )
                    continue

                # Save optimization metrics to optimization_result.json under window_id
                out_path = self.get_output_path(
                    strategy_name,
                    symbol,
                    self.start_date,
                    self.end_date,
                )
                self.logger.info(
                    f"Saving optimization results for {symbol} {strategy_name} to {out_path}"
                )
                # Load existing results if present
                if out_path.exists():
                    with open(out_path, "r") as f:
                        opt_results = json.load(f)
                else:
                    opt_results = {}

                if self.window_id not in opt_results:
                    opt_results[self.window_id] = {}

                opt_results[self.window_id]["optimization"] = (
                    optimization_result  # or "test" for test results
                )

                opt_results[self.window_id]["window"] = {
                    "start_date": str(self.start_date),
                    "end_date": str(self.end_date),
                }

                # Save the updated results
                with open(out_path, "w") as f:
                    json.dump(opt_results, f, indent=2, default=str)

                results.setdefault(symbol, {})[strategy_name] = {
                    self.window_id: optimization_result
                }

        return results

    def get_output_path(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ):
        """Get the output path for the optimization results JSON file."""
        out_dir = self.stage_data_manager.get_extended_path(
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

        raw_results = await self.executor.run_backtest(
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

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
