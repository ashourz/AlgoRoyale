import asyncio
from logging import Logger

from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)


class PipelineCoordinator:
    """Coordinator for the backtest pipeline.
    This class orchestrates the execution of the backtest pipeline stages,
    including walk-forward evaluation and performance analysis.

    Parameters:
        walk_forward_coordinator (WalkForwardCoordinator): Coordinator for walk-forward evaluation.
        walk_forward_evaluation_coordinator (WalkForwardEvaluationCoordinator): Coordinator for evaluation of walk-forward results.
        logger (Logger): Logger instance for logging messages.
    """

    def __init__(
        self,
        walk_forward_coordinator: WalkForwardCoordinator,
        # walk_forward_evaluation_coordinator: WalkForwardEvaluationCoordinator,
        logger: Logger,
    ):
        self.logger = logger
        self.walk_forward_coordinator = walk_forward_coordinator
        # self.walk_forward_evaluation_coordinator = walk_forward_evaluation_coordinator

    async def run_async(self):
        try:
            self.logger.info("Starting Backtest Pipeline...")
            # Run the pipeline stages in sequence
            await self.run_pipeline()
            self.logger.info("Backtest Pipeline completed successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    async def run_pipeline(
        self,
    ):
        try:
            self.walk_forward_coordinator.run()
            # self.walk_forward_evaluation_coordinator.run()
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return False

    def run(self):
        return asyncio.run(self.run_async())
