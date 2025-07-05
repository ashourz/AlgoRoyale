from datetime import datetime
from logging import Logger
from typing import Optional, Sequence

from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
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
        stage: BacktestStage enum value indicating the stage of the backtest.
        logger: Logger instance.
        strategy_combinators: List of strategy combinator classes to use.
    """

    def __init__(
        self,
        stage: BacktestStage,
        data_loader: SymbolStrategyDataLoader,
        data_preparer: StageDataPreparer,
        strategy_combinators: Sequence[type[BaseStrategyCombinator]],
        logger: Logger,
    ):
        """Coordinator for the backtest stage."""
        super().__init__()
        self.stage = stage
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.strategy_combinators = strategy_combinators
        self.logger = logger

    async def run(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        self.start_date = start_date
        self.end_date = end_date

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

        # Prepare the data for processing
        self.logger.info(f"stage:{self.stage} starting data preparation.")
        prepared_data = self.data_preparer.normalize_stage_data(
            stage=self.stage, data=data
        )
        if not prepared_data:
            self.logger.error(f"No data prepared for stage:{self.stage}")
            return False

        # Process the prepared data
        self.logger.info(f"stage:{self.stage} starting data processing.")
        processed_data = await self._process(prepared_data)

        if not processed_data:
            self.logger.error(f"Processing failed for stage:{self.stage}")
            return False

        # Write the processed data to disk
        self.logger.info(f"stage:{self.stage} starting data writing.")
        await self._write(
            stage=self.stage,
            processed_data=processed_data,
        )
        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True
