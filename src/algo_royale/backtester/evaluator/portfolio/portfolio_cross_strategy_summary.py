import json
from pathlib import Path

from algo_royale.logging.loggable import Loggable


class PortfolioCrossStrategySummary:
    """
    Aggregates all strategy evaluation_result.json files for a portfolio and writes summary_result.json.
    """

    def __init__(
        self,
        logger: Loggable,
        evaluation_filename: str = "evaluation_result.json",
        output_filename: str = "summary_result.json",
    ):
        self.logger = logger
        self.evaluation_filename = evaluation_filename
        self.output_filename = output_filename

    def run(
        self,
        symbol_dir: Path,
    ):
        if not symbol_dir.is_dir():
            self.logger.warning(f"Provided symbol_dir is not a directory: {symbol_dir}")
            return None
        strategy_results = []
        for strategy_dir in sorted(symbol_dir.iterdir()):
            if not strategy_dir.is_dir():
                continue
            self.logger.debug(
                f"Processing strategy directory: {strategy_dir} | {self.evaluation_filename}"
            )
            eval_path = strategy_dir / self.evaluation_filename
            if not eval_path.exists():
                self.logger.warning(f"No evaluation_result.json found: {eval_path}")
                continue
            try:
                with open(eval_path) as f:
                    eval_json = json.load(f)
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in {eval_path}, skipping file.")
                continue
            eval_json["strategy"] = strategy_dir.name
            strategy_results.append(eval_json)

        if not strategy_results:
            self.logger.warning(f"No strategy evaluation results found in {symbol_dir}")
            return None

        # Find best strategy by viability_score, then param_consistency
        best = max(
            strategy_results,
            key=lambda r: (r.get("viability_score", 0), r.get("param_consistency", 0)),
        )

        summary = {
            "summary": best.get("summary", {}),
            "n_windows": best.get("n_windows", 0),
            "metric_type": best.get("metric_type", "both"),
            "viability_score": best.get("viability_score", 0),
            "is_viable": best.get("is_viable", False),
            "most_common_best_params": best.get("most_common_best_params", {}),
            "param_consistency": best.get("param_consistency", 0),
            "window_params": best.get("window_params", []),
            "strategy": best.get("strategy"),
        }
        out_path = symbol_dir / self.output_filename
        with open(out_path, "w") as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"Wrote cross-strategy summary to {out_path}")
        return summary
