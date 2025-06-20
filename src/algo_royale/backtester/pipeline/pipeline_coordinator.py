import asyncio
from logging import Logger

from algo_royale.backtester.evaluator.strategy.strategy_evaluation_coordinator import (
    StrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
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
        strategy_evaluation_coordinator (StrategyEvaluationCoordinator): Coordinator for strategy evaluation.
        symbol_evaluation_coordinator (SymbolEvaluationCoordinator): Coordinator for symbol evaluation.
        logger (Logger): Logger instance for logging messages.
    """

    def __init__(
        self,
        walk_forward_coordinator: WalkForwardCoordinator,
        strategy_evaluation_coordinator: StrategyEvaluationCoordinator,
        symbol_evaluation_coordinator: SymbolEvaluationCoordinator,
        logger: Logger,
    ):
        self.logger = logger
        self.walk_forward_coordinator = walk_forward_coordinator
        self.strategy_evaluation_coordinator = strategy_evaluation_coordinator
        self.symbol_evaluation_coordinator = symbol_evaluation_coordinator

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
            await self.walk_forward_coordinator.run_async()
            self.strategy_evaluation_coordinator.run()
            self.symbol_evaluation_coordinator.run()
            self.logger.info("Pipeline stages completed successfully.")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return False

    def run(self):
        return asyncio.run(self.run_async())
