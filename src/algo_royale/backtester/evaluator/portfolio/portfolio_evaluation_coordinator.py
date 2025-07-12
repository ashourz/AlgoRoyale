import json
from pathlib import Path
from algo_royale.logging.loggable import Loggable

from algo_royale.logging.logger_factory import mockLogger


class PortfolioEvaluationCoordinator:
    """
    Aggregates and compares walk-forward evaluation results across all portfolio strategies for each symbol,
    and selects the best strategy based on viability_score and param_consistency.
    Writes a detailed summary for each symbol and a global summary for all recommendations.
    Parameters:
        optimization_root (Path): Root directory containing symbol directories with strategy evaluations.
        strategy_window_evaluation_json_filename (str): Name of the JSON file containing walk-forward evaluation
            results for each strategy.
        strategy_summary_json_filename (str): Name of the JSON file to write the summary report for
            each symbol.
        global_summary_json_filename (str): Name of the JSON file to write the global summary report.
        viability_threshold (float): Minimum viability score for a strategy to be considered viable.
    """

    def __init__(
        self,
        logger: Loggable,
        optimization_root: str,
        strategy_window_evaluation_json_filename: str,
        strategy_summary_json_filename: str,
        global_summary_json_filename: str,
        viability_threshold: float = 0.75,
    ):
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)

        self.evaluation_json_filename = strategy_window_evaluation_json_filename
        self.summary_json_filename = strategy_summary_json_filename
        self.global_summary_json_filename = global_summary_json_filename
        self.viability_threshold = viability_threshold
        self.logger = logger

    def run(self):
        try:
            global_summary = {}
            self.logger.info("Starting portfolio evaluation...")
            # Loop over all symbol directories
            for symbol_dir in self.optimization_root.iterdir():
                try:
                    if not symbol_dir.is_dir():
                        continue
                    symbol = symbol_dir.name
                    self.logger.info(f"Evaluating symbol: {symbol}")
                    strategy_dirs = [d for d in symbol_dir.iterdir() if d.is_dir()]
                    results = []
                    for strat_dir in strategy_dirs:
                        eval_path = strat_dir / self.evaluation_json_filename
                        if eval_path.exists():
                            self.logger.debug(f"Loading evaluation: {eval_path}")
                            with open(eval_path) as f:
                                report = json.load(f)
                                report["strategy"] = strat_dir.name
                                results.append(report)
                        else:
                            self.logger.debug(f"No evaluation file found: {eval_path}")

                    if not results:
                        self.logger.warning(f"No evaluation results found for {symbol}")
                        continue

                    # Filter only viable strategies
                    viable_strategies = [
                        r
                        for r in results
                        if r.get("viability_score", 0) >= self.viability_threshold
                    ]

                    if viable_strategies:
                        # Sort by viability_score, then by param_consistency
                        best = max(
                            viable_strategies,
                            key=lambda r: (
                                r.get("viability_score", 0),
                                r.get("param_consistency", 0),
                            ),
                        )
                        rationale = (
                            f"Selected for highest viability_score (={best['viability_score']})"
                            f" and parameter consistency (={best.get('param_consistency', 0)})"
                        )
                        self.logger.info(
                            f"Selected strategy for {symbol}: {best['strategy']} "
                            f"(viability_score={best['viability_score']}, param_consistency={best.get('param_consistency', 0)})"
                        )
                    else:
                        # If no viable strategy, pick the one with highest viability_score anyway
                        best = max(results, key=lambda r: r.get("viability_score", 0))
                        rationale = (
                            f"No viable strategy found (threshold={self.viability_threshold}). "
                            f"Selected best available by viability_score (={best['viability_score']})."
                        )
                        self.logger.warning(
                            f"No viable strategy found for {symbol}. "
                            f"Best available: {best['strategy']} (viability_score={best['viability_score']})"
                        )

                    # Prepare detailed summary
                    summary = {
                        "symbol": symbol,
                        "recommended_strategy": best["strategy"],
                        "viability_score": best.get("viability_score"),
                        "param_consistency": best.get("param_consistency"),
                        "metrics": {
                            k: v
                            for k, v in best.items()
                            if k
                            not in [
                                "strategy",
                                "allocation_params",
                                "viability_score",
                                "param_consistency",
                            ]
                        },
                        "allocation_params": best.get("allocation_params", {}),
                        "rationale": rationale,
                    }
                    global_summary[symbol] = summary

                    # Write a summary report for the symbol
                    summary_path = symbol_dir / self.summary_json_filename
                    with open(summary_path, "w") as f:
                        json.dump(summary, f, indent=2)
                    self.logger.info(
                        f"Portfolio symbol evaluation report written to {summary_path}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Error during evaluation for symbol {symbol}: {e}",
                        exc_info=True,
                    )
                    continue

            # Write a global summary file
            global_summary_path = (
                self.optimization_root / self.global_summary_json_filename
            )
            with open(global_summary_path, "w") as f:
                json.dump(global_summary, f, indent=2)
            self.logger.info(
                f"Global portfolio evaluation summary written to {global_summary_path}"
            )
        except Exception as e:
            self.logger.error(f"Error during portfolio evaluation: {e}", exc_info=True)
            raise e


def mockPortfolioEvaluationCoordinator(
    optimization_root: str = "mock_optimization_root",
    strategy_window_evaluation_json_filename: str = "mock_evaluation.json",
    strategy_summary_json_filename: str = "mock_summary.json",
    global_summary_json_filename: str = "mock_global_summary.json",
    viability_threshold: float = 0.75,
) -> PortfolioEvaluationCoordinator:
    """
    Create a mock PortfolioEvaluationCoordinator for testing purposes.
    """
    logger = mockLogger()
    return PortfolioEvaluationCoordinator(
        logger=logger,
        optimization_root=optimization_root,
        strategy_window_evaluation_json_filename=strategy_window_evaluation_json_filename,
        strategy_summary_json_filename=strategy_summary_json_filename,
        global_summary_json_filename=global_summary_json_filename,
        viability_threshold=viability_threshold,
    )
