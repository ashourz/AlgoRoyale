from logging import Logger
from typing import Sequence

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.executor.base_backtest_executor import BacktestExecutor
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)


class BaseOptimizationStageCoordinator(StageCoordinator):
    """
    Base class for strategy optimization stage coordinators.
    Subclasses must implement process().
    Parameters:
        data_loader: Data loader for the stage.
        data_preparer: Data preparer for the stage.
        data_writer: Data writer for the stage.
        stage_data_manager: Stage data manager.
        strategy_factory: Strategy factory for creating strategies.
        stage: BacktestStage enum value indicating the stage of the backtest.
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
        stage: BacktestStage,
        logger: Logger,
        executor: BacktestExecutor,
        evaluator: BacktestEvaluator,
        strategy_combinators: Sequence[type[BaseStrategyCombinator]],
    ):
        """Coordinator for the backtest stage."""
        super().__init__(
            stage=stage,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_combinators = strategy_combinators
        self.executor = executor
        self.evaluator = evaluator

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
