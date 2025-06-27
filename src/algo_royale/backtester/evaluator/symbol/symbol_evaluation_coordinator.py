import json
from logging import Logger
from pathlib import Path


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
        logger: Logger,
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
                        report = json.load(f)
                        report["strategy"] = strat_dir.name
                        results.append(report)

            if not results:
                print(f"No evaluation results found for {symbol}")
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
                print(
                    f"Selected strategy for {symbol}: {best['strategy']} "
                    f"(viability_score={best['viability_score']}, param_consistency={best.get('param_consistency', 0)})"
                )
            else:
                # If no viable strategy, pick the one with highest viability_score anyway
                best = max(results, key=lambda r: r.get("viability_score", 0))
                print(
                    f"No viable strategy found for {symbol}. "
                    f"Best available: {best['strategy']} (viability_score={best['viability_score']})"
                )

            # Write a summary report for the symbol
            summary_path = symbol_dir / self.summary_json_filename
            with open(summary_path, "w") as f:
                json.dump(best, f, indent=2)
            print(f"Symbol evaluation report written to {summary_path}")
