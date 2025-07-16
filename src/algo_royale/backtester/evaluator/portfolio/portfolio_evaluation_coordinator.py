import json
from pathlib import Path

from algo_royale.logging.loggable import Loggable
from algo_royale.logging.logger_factory import mockLogger


class PortfolioEvaluationCoordinator:
    """
    Aggregates and compares walk-forward evaluation results across all portfolio strategies for each strategy,
    and selects the best strategy based on viability_score and param_consistency.
    Writes a detailed summary for each strategy and a global summary for all recommendations.
    Parameters:
        optimization_root (Path): Root directory containing strategy directories with strategy evaluations.
        strategy_window_evaluation_json_filename (str): Name of the JSON file containing walk-forward evaluation
            results for each strategy.
        strategy_summary_json_filename (str): Name of the JSON file to write the summary report for
            each strategy.
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
            # Loop over all strategy directories
            for strategy_dir in self.optimization_root.iterdir():
                try:
                    self.logger.debug(f"Found strategy directory: {strategy_dir}")
                    if not strategy_dir.is_dir():
                        self.logger.debug(f"Skipping non-directory: {strategy_dir}")
                        continue
                    strategy = strategy_dir.name
                    self.logger.info(f"Evaluating strategy: {strategy}")
                    strategy_dirs = [d for d in strategy_dir.iterdir() if d.is_dir()]
                    if not strategy_dirs:
                        self.logger.warning(
                            f"No strategy directories found for strategy {strategy}. Skipping."
                        )
                        continue
                    self.logger.debug(
                        f"Found {len(strategy_dirs)} strategy directories for strategy {strategy}."
                    )
                    results = []
                    for strat_dir in strategy_dirs:
                        self.logger.debug(
                            f"Processing strategy directory: {strat_dir} / {self.evaluation_json_filename}"
                        )
                        # Load evaluation results for this strategy
                        eval_path = strat_dir / self.evaluation_json_filename
                        if eval_path.exists():
                            self.logger.debug(f"Loading evaluation: {eval_path}")
                            with open(eval_path) as f:
                                report = json.load(f)
                                report["strategy"] = strat_dir.name
                                results.append(report)
                        else:
                            self.logger.debug(f"No evaluation file found: {eval_path}")

                    self.logger.debug(
                        f"Processing strategy summary directory: {strat_dir} / {self.summary_json_filename}"
                    )
                    summary_path = strategy_dir / self.summary_json_filename
                    if not results:
                        self.logger.warning(
                            f"No evaluation results found for {strategy}"
                        )
                        # Write a default summary for the strategy
                        summary = {
                            "strategy": strategy,
                            "recommended_strategy": None,
                            "viability_score": None,
                            "param_consistency": None,
                            "metrics": {},
                            "allocation_params": {},
                            "rationale": "No evaluation results found for this strategy.",
                            "status": "no_results",
                        }
                        with open(summary_path, "w") as f:
                            json.dump(summary, f, indent=2)
                        global_summary[strategy] = summary
                        continue

                    # Filter only viable strategies
                    viable_strategies = [
                        r
                        for r in results
                        if r.get("viability_score", 0) >= self.viability_threshold
                    ]

                    if viable_strategies:
                        self.logger.info(
                            f"Found {len(viable_strategies)} viable strategies for {strategy}."
                        )
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
                            f"Selected strategy for {strategy}: {best['strategy']} "
                            f"(viability_score={best['viability_score']}, param_consistency={best.get('param_consistency', 0)})"
                        )
                    else:
                        self.logger.warning(
                            f"No viable strategies found for {strategy} (threshold={self.viability_threshold})."
                        )
                        # If no viable strategy, pick the one with highest viability_score anyway
                        best = max(results, key=lambda r: r.get("viability_score", 0))
                        rationale = (
                            f"No viable strategy found (threshold={self.viability_threshold}). "
                            f"Selected best available by viability_score (={best['viability_score']})."
                        )
                        self.logger.warning(
                            f"No viable strategy found for {strategy}. "
                            f"Best available: {best['strategy']} (viability_score={best['viability_score']})"
                        )

                    # Prepare detailed summary
                    summary = {
                        "strategy": strategy,
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
                        "status": "ok",
                    }
                    global_summary[strategy] = summary

                    # Write a summary report for the strategy
                    with open(summary_path, "w") as f:
                        json.dump(summary, f, indent=2)
                    self.logger.info(
                        f"Portfolio strategy evaluation report written to {summary_path}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Error during evaluation for strategy {strategy}: {e}",
                        exc_info=True,
                    )
                    # Still write a summary file for the strategy with error info
                    summary = {
                        "strategy": strategy if "strategy" in locals() else None,
                        "recommended_strategy": None,
                        "viability_score": None,
                        "param_consistency": None,
                        "metrics": {},
                        "allocation_params": {},
                        "rationale": f"Error during evaluation: {e}",
                        "status": "error",
                    }
                    with open(strategy_dir / self.summary_json_filename, "w") as f:
                        json.dump(summary, f, indent=2)
                    global_summary[strategy] = summary
                    continue

            # Write a global summary file
            global_summary_path = (
                self.optimization_root / self.global_summary_json_filename
            )
            if not global_summary:
                # Write a default global summary if no results at all
                global_summary_obj = {
                    "status": "no_results",
                    "message": "No evaluation results found for any strategy.",
                    "results": {},
                }
            else:
                global_summary_obj = {
                    "status": "ok",
                    "message": "Portfolio evaluation completed.",
                    "results": global_summary,
                }
            with open(global_summary_path, "w") as f:
                json.dump(global_summary_obj, f, indent=2)
            self.logger.info(
                f"Global portfolio evaluation summary written to {global_summary_path}"
            )
        except Exception as e:
            self.logger.error(f"Error during portfolio evaluation: {e}", exc_info=True)
            # Write a global summary file with error info
            global_summary_path = (
                self.optimization_root / self.global_summary_json_filename
            )
            global_summary_obj = {
                "status": "error",
                "message": f"Error during portfolio evaluation: {e}",
                "results": {},
            }
            with open(global_summary_path, "w") as f:
                json.dump(global_summary_obj, f, indent=2)
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
