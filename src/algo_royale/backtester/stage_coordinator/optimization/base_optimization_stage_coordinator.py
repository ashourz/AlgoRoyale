from datetime import datetime
from typing import Sequence
from algo_royale.logging.loggable import Loggable

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)


class BaseOptimizationStageCoordinator(StageCoordinator):
    """
    Base class for strategy optimization stage coordinators.
    Subclasses must implement process().
    Parameters:
        stage: BacktestStage enum value indicating the stage of the backtest.
        data_loader: Data loader for the stage.
        stage_data_manager: StageDataManager for managing stage data.
        strategy_combinators: List of strategy combinator classes to use.
        logger: Loggable instance.
    """

    def __init__(
        self,
        stage: BacktestStage,
        data_loader: SymbolStrategyDataLoader,
        stage_data_manager: StageDataManager,
        strategy_combinators: Sequence[type[BaseStrategyCombinator]],
        logger: Loggable,
    ):
        """Coordinator for the backtest stage."""
        super().__init__()
        self.stage = stage
        self.data_loader = data_loader
        self.stage_data_manager = stage_data_manager
        self.strategy_combinators = strategy_combinators
        self.logger = logger

    async def run(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> bool:
        """
        Orchestrate the stage: load, process, write.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.window_id = self.stage_data_manager.get_window_id(
            start_date=self.start_date, end_date=self.end_date
        )

        self.logger.info(
            f"Starting stage: {self.stage} | start_date: {start_date} | end_date: {end_date}"
        )
        if not self.stage.input_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            raise ValueError(
                f"Stage {self.stage} has no incoming stage defined. Cannot proceed with data loading."
            )

        # Load the data from the input stage
        self.logger.info(f"stage:{self.stage} starting data loading.")
        data = await self.data_loader.load_data(
            stage=self.stage.input_stage,
            start_date=self.start_date,
            end_date=self.end_date,
            reverse_pages=True,
        )
        if not data:
            self.logger.error(f"No data loaded from stage:{self.stage.input_stage}")
            return False

        # Process the data
        self.logger.info(f"stage:{self.stage} starting data processing.")
        processed_data = await self._process_and_write(data)

        if not processed_data:
            self.logger.error(f"Processing failed for stage:{self.stage}")
            return False

        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True
