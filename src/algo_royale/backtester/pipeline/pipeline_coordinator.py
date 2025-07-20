import asyncio

from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_coordinator import (
    StrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from algo_royale.logging.loggable import Loggable


class PipelineCoordinator:
    """Coordinator for the backtest pipeline.
    This class orchestrates the execution of the backtest pipeline stages,
    including walk-forward evaluation and performance analysis.

    Parameters:
        strategy_walk_forward_coordinator (WalkForwardCoordinator): Coordinator for strategy walk-forward evaluation.
        portfolio_walk_forward_coordinator (WalkForwardCoordinator): Coordinator for portfolio walk-forward evaluation.
        strategy_evaluation_coordinator (StrategyEvaluationCoordinator): Coordinator for strategy performance evaluation.
        symbol_evaluation_coordinator (SymbolEvaluationCoordinator): Coordinator for symbol performance evaluation.
        logger (Logger): Logger instance for logging messages and errors.
    """

    def __init__(
        self,
        strategy_walk_forward_coordinator: WalkForwardCoordinator,
        portfolio_walk_forward_coordinator: WalkForwardCoordinator,
        strategy_evaluation_coordinator: StrategyEvaluationCoordinator,
        symbol_evaluation_coordinator: SymbolEvaluationCoordinator,
        portfolio_evaluation_coordinator: PortfolioEvaluationCoordinator,
        logger: Loggable,
    ):
        self.logger = logger
        self.strategy_walk_forward_coordinator = strategy_walk_forward_coordinator
        self.portfolio_walk_forward_coordinator = portfolio_walk_forward_coordinator
        self.strategy_evaluation_coordinator = strategy_evaluation_coordinator
        self.symbol_evaluation_coordinator = symbol_evaluation_coordinator
        self.portfolio_evaluation_coordinator = portfolio_evaluation_coordinator

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
            self.logger.info("Running pipeline stages...")
            # await self.strategy_walk_forward_coordinator.run_async()
            # self.strategy_evaluation_coordinator.run()
            self.symbol_evaluation_coordinator.run()
            # await self.portfolio_walk_forward_coordinator.run_async()
            # self.portfolio_evaluation_coordinator.run()
            self.logger.info("Pipeline stages completed successfully.")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return False

    def run(self):
        return asyncio.run(self.run_async())
