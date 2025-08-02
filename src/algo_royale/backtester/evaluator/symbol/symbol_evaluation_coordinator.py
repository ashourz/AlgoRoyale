import json
from pathlib import Path

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.logging.loggable import Loggable
from algo_royale.logging.logger_factory import mockLogger


class SymbolEvaluationCoordinator:
    """
    Aggregates and compares walk-forward evaluation results across all strategies for each symbol,
    and selects the best strategy based on viability_score and param_consistency.
    Parameters:
        optimization_root (Path): Root directory containing symbol directories with strategy evaluations.
        evaluation_json_filename (str): Name of the JSON file containing walk-forward evaluation results.
        summary_json_filename (str): Name of the JSON file to write the summary report for each symbol.
        viability_threshold (float): Minimum viability score for a strategy to be considered viable.
    """

    def __init__(
        self,
        optimization_root: str,
        evaluation_json_filename: str,
        summary_json_filename: str,
        logger: Loggable,
        viability_threshold: float = 0.75,
    ):
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it doesn't exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)

        self.evaluation_json_filename = evaluation_json_filename
        self.summary_json_filename = summary_json_filename
        self.viability_threshold = viability_threshold
        self.logger = logger

    def run(self):
        self.logger.info("Starting symbol evaluation...")
        # Loop over all symbol directories
        try:
            for symbol_dir in self.optimization_root.iterdir():
                self.logger.info(f"Evaluating symbol directory: {symbol_dir}")
                if not symbol_dir.is_dir():
                    continue
                symbol = symbol_dir.name
                strategy_dirs = [d for d in symbol_dir.iterdir() if d.is_dir()]
                results = []
                for strat_dir in strategy_dirs:
                    self.logger.debug(f"Checking strategy directory: {strat_dir}")
                    eval_path = strat_dir / self.evaluation_json_filename
                    if eval_path.exists():
                        with open(eval_path) as f:
                            loaded_results = json.load(f)
                        if not self._validate_input_report(loaded_results):
                            self.logger.warning(
                                f"Invalid evaluation report for {symbol} in {strat_dir}. Skipping."
                            )
                            continue
                        report = loaded_results
                        report["strategy"] = strat_dir.name
                        results.append(report)

                if not results:
                    self.logger.warning(
                        f"No evaluation results found for {symbol} in {symbol_dir}. Skipping."
                    )
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
                    # Log the selected strategy
                    self.logger.info(
                        f"Selected strategy for {symbol}: {best['strategy']} "
                        f"(viability_score={best['viability_score']}, "
                        f"param_consistency={best.get('param_consistency', 0)})"
                    )
                else:
                    # If no viable strategy, pick the one with highest viability_score anyway
                    best = max(results, key=lambda r: r.get("viability_score", 0))
                    self.logger.warning(
                        f"No viable strategy found for {symbol}. "
                        f"Best available: {best['strategy']} (viability_score={best['viability_score']})"
                    )

                # Write a summary report for the symbol
                summary_path = symbol_dir / self.summary_json_filename
                with open(summary_path, "w") as f:
                    json.dump(best, f, indent=2)
                self.logger.info(
                    f"Summary report for {symbol} written to {summary_path}"
                )
        except Exception as e:
            self.logger.error(f"Error during symbol evaluation: {e}")
            raise e

    def _validate_input_report(self, report: dict) -> None:
        """
        Validate the input report structure.
        Args:
            report (dict): The evaluation report to validate.
        Raises:
            ValueError: If the report does not contain required fields.
        """
        try:
            validation_method = BacktestStage.SYMBOL_EVALUATION.input_validation_fn
            if not callable(validation_method):
                raise ValueError(
                    f"Validation method {validation_method} is not callable."
                )
            return validation_method(report, self.logger)
        except Exception as e:
            self.logger.error(
                f"Error validating input report for symbol evaluation: {e}"
            )
            raise e


def mockSymbolEvaluationCoordinator():
    """
    Mock version of SymbolEvaluationCoordinator for testing purposes.
    """
    logger = mockLogger()
    return SymbolEvaluationCoordinator(
        optimization_root="mock/optimization/root",
        evaluation_json_filename="mock_evaluation.json",
        summary_json_filename="mock_summary.json",
        logger=logger,
        viability_threshold=0.75,
    )
