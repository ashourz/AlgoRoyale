import json
from pathlib import Path
from typing import List

from .walk_forward_evaluator import WalkForwardEvaluator


class WalkForwardEvaluationStageCoordinator:
    def __init__(self, optimization_root: str, metric_type: str = "test"):
        """
        optimization_root: path to the root directory containing optimization results for all strategies/symbols
        metric_type: "test", "optimization", or "both"
        """
        self.optimization_root = Path(optimization_root)
        self.metric_type = metric_type

    def find_optimization_result_files(self) -> List[Path]:
        """Recursively find all optimization_result.json files under the root."""
        return list(self.optimization_root.rglob("optimization_result.json"))

    def evaluate_and_write_reports(self):
        """Evaluate all found optimization results and write evaluation reports."""
        for opt_json_path in self.find_optimization_result_files():
            symbol_dir = opt_json_path.parent
            try:
                evaluator = WalkForwardEvaluator(
                    str(opt_json_path), metric_type=self.metric_type
                )
                summary = evaluator.summary()
                viability_score = evaluator.viability_score()
                is_viable = evaluator.is_viable()
                report = {
                    "summary": summary,
                    "viability_score": viability_score,
                    "is_viable": is_viable,
                    "metric_type": self.metric_type,
                }
                eval_path = symbol_dir / "walk_forward_evaluation.json"
                with open(eval_path, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"Wrote evaluation report: {eval_path}")
            except Exception as e:
                print(f"Failed to evaluate {opt_json_path}: {e}")


# Example usage:
# coordinator = WalkForwardEvaluationStageCoordinator(
#     optimization_root="c:/Users/ashou/AlgoRoyale/data/optimization/BollingerBandsStrategy",
#     metric_type="both"
# )
# coordinator.evaluate_and_write_reports()
