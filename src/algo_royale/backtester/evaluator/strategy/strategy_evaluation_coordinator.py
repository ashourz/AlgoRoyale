import json
from logging import Logger
from pathlib import Path
from typing import List

import numpy as np

from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)

from .strategy_evaluator import StrategyEvaluator


class StrategyEvaluationCoordinator:
    """Coordinator for evaluating walk-forward optimization results.
    This class finds all optimization result files, evaluates them,
    and writes the evaluation reports to JSON files.
    It supports different evaluation types: test, optimization, or both.
    Parameters:
        logger (Logger): Logger instance for logging messages.
        optimization_root_path (Path): Path to the root directory containing optimization results.
        evaluation_type (WalkForwardEvaluationType): Type of evaluation to perform (test, optimization, or both).
        optimization_json_filename (str): Name of the optimization result JSON file.
        evaluation_json_filename (str): Name of the evaluation report JSON file.
    """

    def __init__(
        self,
        logger: Logger,
        optimization_root_path: Path,
        evaluation_type: StrategyEvaluationType,
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
        self.opt_root_path = Path(optimization_root_path)
        self.evaluation_type = evaluation_type
        self.opt_result_json_filename = optimization_json_filename
        self.eval_json_filename = evaluation_json_filename
        self.logger = logger

    def run(self):
        # Loop over each symbol directory
        for symbol_dir in self.opt_root_path.iterdir():
            if not symbol_dir.is_dir():
                continue
            self.logger.info(f"Processing symbol: {symbol_dir.name}")
            # Loop over each strategy directory within the symbol
            for strategy_dir in symbol_dir.iterdir():
                if not strategy_dir.is_dir():
                    continue
                self.logger.info(f"  Processing strategy: {strategy_dir.name}")
                self._evaluate_strategy_dir(strategy_dir)

    def _evaluate_strategy_dir(self, strategy_dir: Path):
        optimization_files = list(strategy_dir.rglob(self.opt_result_json_filename))
        if not optimization_files:
            self.logger.info(
                f"No optimization result files found in {strategy_dir}. Skipping evaluation."
            )
            return

        all_metrics = []
        window_params = []
        for opt_json_path in optimization_files:
            if not opt_json_path.is_file():
                continue
            try:
                self.logger.info(f"Evaluating {opt_json_path}...")
                evaluator = StrategyEvaluator(
                    opt_json_path, metric_type=self.evaluation_type
                )
                all_metrics.extend(evaluator.metrics)
                for window, data in evaluator.results.items():
                    best_params = data.get("optimization", {}).get("best_params")
                    if best_params:
                        window_params.append(json.dumps(best_params, sort_keys=True))
            except Exception as e:
                self.logger.error(
                    f"Error evaluating {opt_json_path}: {e}. Skipping this file."
                )

        if not all_metrics:
            self.logger.warning("No metrics found in any optimization result files.")
            return

        keys = [k for k in all_metrics[0] if k not in ("window", "type")]
        summary = {}
        for k in keys:
            values = [m[k] for m in all_metrics if k in m]
            summary[k] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }

        def viability_score(summary, thresholds=None):
            if not summary:
                return 0
            if thresholds is None:
                thresholds = {
                    "total_return": 0.05,
                    "sharpe_ratio": 0.5,
                    "win_rate": 0.5,
                    "max_drawdown": 0.5,
                }
            score = 0
            checks = 0
            for metric in ["total_return", "sharpe_ratio", "win_rate"]:
                if metric in summary:
                    checks += 1
                    if summary[metric]["mean"] >= thresholds[metric]:
                        score += 1
            if "max_drawdown" in summary:
                checks += 1
                if summary["max_drawdown"]["mean"] <= thresholds["max_drawdown"]:
                    score += 1
            return score / checks if checks > 0 else 0

        vs = viability_score(summary)
        is_viable = vs >= 0.75

        from collections import Counter

        if window_params:
            param_counts = Counter(window_params)
            most_common_params, count = param_counts.most_common(1)[0]
            most_common_params = json.loads(most_common_params)
            param_consistency = count / len(window_params)
        else:
            most_common_params = None
            param_consistency = 0

        report = {
            "summary": summary,
            "n_windows": len(all_metrics),
            "metric_type": str(self.evaluation_type),
            "viability_score": vs,
            "is_viable": is_viable,
            "most_common_best_params": most_common_params,
            "param_consistency": param_consistency,
            "window_params": [json.loads(p) for p in window_params],
        }

        # Write to the strategy directory
        eval_path = strategy_dir / self.eval_json_filename
        with open(eval_path, "w") as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"Aggregated evaluation report written to {eval_path}.")

    def _find_optimization_result_files(self) -> List[Path]:
        """Recursively find all optimization_result.json files under the root."""
        return list(self.opt_root_path.rglob(self.opt_result_json_filename))

    def evaluate_results(self, opt_json_path: Path) -> dict:
        """Evaluate a single optimization result file."""
        evaluator = StrategyEvaluator(opt_json_path, metric_type=self.evaluation_type)
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

    def write_aggregated_evaluation_report(self, out_dir: Path, report: dict):
        """Write the aggregated evaluation report to a JSON file at the root."""
        eval_path = out_dir / self.eval_json_filename
        with open(eval_path, "w") as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"Aggregated evaluation report written to {eval_path}.")


# Example usage:
# coordinator = WalkForwardEvaluationCoordinator(
#     optimization_root="c:/Users/ashou/AlgoRoyale/data/optimization/BollingerBandsStrategy",
#     metric_type="both"
# )
# coordinator.evaluate_and_write_reports()
