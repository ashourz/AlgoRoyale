import json
from pathlib import Path


class SymbolEvaluationCoordinator:
    """
    Aggregates and compares walk-forward evaluation results across all strategies for a symbol,
    and selects the best strategy based on viability_score and param_consistency.
    """

    def __init__(
        self,
        symbol: str,
        optimization_root: Path,
        evaluation_json_filename: str = "walk_forward_evaluation.json",
        summary_json_filename: str = "symbol_evaluation.json",
        viability_threshold: float = 0.75,
    ):
        self.symbol = symbol
        self.optimization_root = Path(optimization_root)
        self.evaluation_json_filename = evaluation_json_filename
        self.summary_json_filename = summary_json_filename
        self.viability_threshold = viability_threshold

    def run(self):
        strategy_dirs = [d for d in self.optimization_root.iterdir() if d.is_dir()]
        results = []
        for strat_dir in strategy_dirs:
            eval_path = strat_dir / self.symbol / self.evaluation_json_filename
            if eval_path.exists():
                with open(eval_path) as f:
                    report = json.load(f)
                    report["strategy"] = strat_dir.name
                    results.append(report)

        if not results:
            print(f"No evaluation results found for {self.symbol}")
            return

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
                f"Selected strategy for {self.symbol}: {best['strategy']} "
                f"(viability_score={best['viability_score']}, param_consistency={best.get('param_consistency', 0)})"
            )
        else:
            # If no viable strategy, pick the one with highest viability_score anyway
            best = max(results, key=lambda r: r.get("viability_score", 0))
            print(
                f"No viable strategy found for {self.symbol}. "
                f"Best available: {best['strategy']} (viability_score={best['viability_score']})"
            )

        # Write a summary report for the symbol
        summary_path = self.optimization_root / self.symbol / self.summary_json_filename
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w") as f:
            json.dump(best, f, indent=2)
        print(f"Symbol evaluation report written to {summary_path}")


# Example usage:
# coordinator = SymbolEvaluationCoordinator(
#     symbol="QUBT",
#     optimization_root=Path("c:/Users/sajit/AlgoRoyale/data/optimization"),
# )
# coordinator.run()
