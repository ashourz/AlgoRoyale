import json
from pathlib import Path
from typing import List

from algo_royale.backtester.walkforward.walk_forward_evaluation_type import (
    WalkForwardEvaluationType,
)

from .walk_forward_evaluator import WalkForwardEvaluator


class WalkForwardEvaluationStageCoordinator:
    def __init__(
        self,
        optimization_root_path: Path,
        evaluation_type: WalkForwardEvaluationType,
        optimization_json_filename: str = "optimization_result.json",
        evaluation_json_filename: str = "walk_forward_evaluation.json",
    ):
        """
        Args:
            optimization_root_path: Path to the root directory containing optimization results.
            evaluation_type: Type of evaluation to perform (test, optimization, or both).
            optimization_result_json_filename: Name of the optimization result JSON file.
            evaluation_json_filename: Name of the evaluation report JSON file.
        """
        self.opt_root_path = optimization_root_path
        self.evaluation_type = evaluation_type
        self.opt_result_json_filename = optimization_json_filename
        self.eval_json_filename = evaluation_json_filename

    def run(self):
        """Run the evaluation process.
        This method finds all optimization result files, evaluates them,
        and writes the evaluation reports.
        """
        for opt_json_path in self._find_optimization_result_files():
            symbol_dir = opt_json_path.parent
            try:
                report = self.evaluate_results(opt_json_path)
                self.write_evaluation_report(symbol_dir, report)
            except Exception as e:
                print(f"Failed to evaluate {opt_json_path}: {e}")

    def _find_optimization_result_files(self) -> List[Path]:
        """Recursively find all optimization_result.json files under the root."""
        return list(self.opt_root_path.rglob(self.opt_result_json_filename))

    def evaluate_results(self, opt_json_path: Path) -> dict:
        """Evaluate a single optimization result file."""
        evaluator = WalkForwardEvaluator(
            opt_json_path, metric_type=self.evaluation_type
        )
        summary = evaluator.summary()
        viability_score = evaluator.viability_score()
        is_viable = evaluator.is_viable()
        report = {
            "summary": summary,
            "viability_score": viability_score,
            "is_viable": is_viable,
            "metric_type": self.evaluation_type,
        }
        return report

    def write_evaluation_report(self, symbol_dir: Path, report: dict):
        """Write the evaluation report to a JSON file."""
        eval_path = symbol_dir / self.eval_json_filename
        with open(eval_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote evaluation report: {eval_path}")


# Example usage:
# coordinator = WalkForwardEvaluationStageCoordinator(
#     optimization_root="c:/Users/ashou/AlgoRoyale/data/optimization/BollingerBandsStrategy",
#     metric_type="both"
# )
# coordinator.evaluate_and_write_reports()
