import json
from pathlib import Path
from typing import List

import numpy as np

from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.logging.logger_factory import mockLogger

from .strategy_evaluator import StrategyEvaluator


class SignalStrategyEvaluationCoordinator:
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
        logger: Loggable,
        optimization_root: str,
        evaluation_type: StrategyEvaluationType,
        optimization_json_filename: str,
        evaluation_json_filename: str,
    ):
        """
        Args:
            optimization_root_path: Path to the root directory containing optimization results.
            evaluation_type: Type of evaluation to perform (test, optimization, or both).
            optimization_result_json_filename: Name of the optimization result JSON file.
            evaluation_json_filename: Name of the evaluation report JSON file.
        """
        self.opt_root_path = Path(optimization_root)
        if not self.opt_root_path.is_dir():
            ## Create the directory if it does not exist
            self.opt_root_path.mkdir(parents=True, exist_ok=True)

        self.evaluation_type = evaluation_type
        self.opt_result_json_filename = optimization_json_filename
        self.eval_json_filename = evaluation_json_filename
        self.logger = logger

    def run(self):
        self.logger.info("Starting strategy evaluation...")
        try:
            # Loop over each symbol directory
            for symbol_dir in self.opt_root_path.iterdir():
                try:
                    self.logger.info(f"Evaluating symbol directory: {symbol_dir}")
                    if not symbol_dir.is_dir():
                        continue
                    self.logger.info(f"Processing symbol: {symbol_dir.name}")
                    # Loop over each strategy directory within the symbol
                    for strategy_dir in symbol_dir.iterdir():
                        try:
                            self.logger.debug(
                                f"Checking strategy directory: {strategy_dir}"
                            )
                            if not strategy_dir.is_dir():
                                continue
                            self.logger.info(
                                f"Processing strategy: {strategy_dir.name}"
                            )
                            self._evaluate_strategy_dir(strategy_dir)
                        except Exception as e:
                            self.logger.error(
                                f"Error processing strategy directory {strategy_dir}: {e}"
                            )
                            continue
                except Exception as e:
                    self.logger.error(
                        f"Error processing symbol directory {symbol_dir}: {e}"
                    )
                    continue
        except Exception as e:
            self.logger.error(f"Error during strategy evaluation: {e}")
            raise e

    def _evaluate_strategy_dir(self, strategy_dir: Path):
        optimization_files = list(strategy_dir.rglob(self.opt_result_json_filename))
        if not optimization_files:
            self.logger.info(
                f"No optimization result files found in {strategy_dir}. Skipping evaluation."
            )
            return
        self.logger.info(
            f"Found {len(optimization_files)} optimization result files in {strategy_dir}."
        )

        all_metrics = []
        window_params = []
        for opt_json_path in optimization_files:
            self.logger.debug(
                f"Path: {opt_json_path} | Is file: {opt_json_path.is_file()} | Is dir: {opt_json_path.is_dir()}"
            )
            if not opt_json_path.is_file():
                self.logger.warning(f"Skipping {opt_json_path} as it is not a file.")
                continue
            self.logger.debug(f"Found optimization result file: {opt_json_path}")
            try:
                self.logger.info(f"Evaluating {opt_json_path}...")
                evaluator = StrategyEvaluator(
                    logger=self.logger, metric_type=self.evaluation_type
                )
                evaluator.load_data(results_path=opt_json_path)
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


def mockStrategyEvaluationCoordinator(
    optimization_root: str = "mock_optimization_root",
    evaluation_type: StrategyEvaluationType = StrategyEvaluationType.TEST,
    optimization_json_filename: str = "mock_optimization.json",
    evaluation_json_filename: str = "mock_evaluation.json",
) -> SignalStrategyEvaluationCoordinator:
    """
    Create a mock StrategyEvaluationCoordinator for testing purposes.
    """
    logger = mockLogger()
    return SignalStrategyEvaluationCoordinator(
        logger=logger,
        optimization_root=optimization_root,
        evaluation_type=evaluation_type,
        optimization_json_filename=optimization_json_filename,
        evaluation_json_filename=evaluation_json_filename,
    )
