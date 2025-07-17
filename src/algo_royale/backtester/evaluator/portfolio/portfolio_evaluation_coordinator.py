from pathlib import Path

from algo_royale.backtester.evaluator.portfolio.portfolio_cross_strategy_summary import (
    PortfolioCrossStrategySummary,
)
from algo_royale.backtester.evaluator.portfolio.portfolio_cross_window_evaluator import (
    PortfolioCrossWindowEvaluator,
)
from algo_royale.logging.loggable import Loggable


class PortfolioEvaluationCoordinator:
    """
    Orchestrates cross-window and cross-strategy evaluation for all portfolio strategies.
    """

    def __init__(
        self,
        logger: Loggable,
        cross_window_evaluator: PortfolioCrossWindowEvaluator,
        cross_strategy_summary: PortfolioCrossStrategySummary,
        optimization_root: str,
        viability_threshold: float = 0.75,
    ):
        self.cross_window_evaluator = cross_window_evaluator
        self.cross_strategy_summary = cross_strategy_summary
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.viability_threshold = viability_threshold
        self.logger = logger

    def run(self):
        self.logger.info("Starting portfolio evaluation...")
        # 1. For each strategy, aggregate all window results into evaluation_result.json
        for strategy_dir in sorted(self.optimization_root.iterdir()):
            if not strategy_dir.is_dir():
                continue
            self.logger.info(f"Aggregating windows for strategy: {strategy_dir.name}")
            self.cross_window_eval.run(strategy_dir=strategy_dir)

        # 2. Aggregate all strategy evaluation_result.json into summary_result.json
        self.logger.info("Aggregating strategy evaluations into summary...")
        self.cross_strategy_summary.run(portfolio_dir=self.optimization_root)
        self.logger.info("Portfolio evaluation completed successfully.")
