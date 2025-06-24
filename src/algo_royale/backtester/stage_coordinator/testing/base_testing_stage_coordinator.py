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
from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class BaseTestingStageCoordinator(StageCoordinator):
    """
    Base class for strategy testing stage coordinators.
    Subclasses must implement process().
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
        strategy_combinators: Sequence[type[SignalStrategyCombinator]],
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

    # Add any shared logic for strategy testing here
