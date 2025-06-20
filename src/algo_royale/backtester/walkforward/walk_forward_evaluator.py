import json
from pathlib import Path

import numpy as np

from algo_royale.backtester.walkforward.walk_forward_evaluation_type import (
    WalkForwardEvaluationType,
)


class WalkForwardEvaluator:
    """
    Class to evaluate the results of a walk-forward optimization.
    It reads the optimization results from a JSON file and computes various metrics.
    """

    def __init__(
        self,
        results_path: Path,
        metric_type: WalkForwardEvaluationType = WalkForwardEvaluationType.BOTH,
    ):
        """
        Args:
            results_path: Path to the JSON file containing optimization results.
            metric_type: Type of metrics to extract (test, optimization, or both).
        """
        with open(results_path, "r") as f:
            self.results = json.load(f)
        self.metric_type = metric_type
        self.metrics = self._extract_metrics()

    def _extract_metrics(self):
        metrics = []
        for window, data in self.results.items():
            if self.metric_type == "both":
                for key in ["optimization", "test"]:
                    if key in data and "metrics" in data[key]:
                        m = data[key]["metrics"].copy()
                        m["window"] = window
                        m["type"] = key
                        metrics.append(m)
            else:
                if self.metric_type in data and "metrics" in data[self.metric_type]:
                    m = data[self.metric_type]["metrics"].copy()
                    m["window"] = window
                    metrics.append(m)
        return metrics

    def summary(self):
        if not self.metrics:
            return {}
        df = {
            k: [m[k] for m in self.metrics if k in m]
            for k in self.metrics[0]
            if k not in ("window", "type")
        }
        summary = {
            k: {
                "mean": np.mean(v),
                "std": np.std(v),
                "min": np.min(v),
                "max": np.max(v),
            }
            for k, v in df.items()
        }
        return summary

    def viability_score(self, thresholds=None):
        if not self.metrics:
            return 0
        if thresholds is None:
            thresholds = {
                "total_return": 0.05,
                "sharpe_ratio": 0.5,
                "win_rate": 0.5,
                "max_drawdown": 0.5,
            }
        summary = self.summary()
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

    def is_viable(self, min_score=0.75):
        return self.viability_score() >= min_score

    def print_report(self):
        print("Walk-Forward Evaluation Report")
        print("=" * 32)
        for m in self.metrics:
            type_str = f" ({m['type']})" if "type" in m else ""
            print(f"Window: {m['window']}{type_str}")
            print(f"  Total Return: {m['total_return']:.3f}")
            print(f"  Sharpe Ratio: {m['sharpe_ratio']:.3f}")
            print(f"  Win Rate: {m['win_rate']:.3f}")
            print(f"  Max Drawdown: {m['max_drawdown']:.3f}")
            print("-" * 32)
        print("Summary Statistics:")
        for k, v in self.summary().items():
            print(
                f"{k}: mean={v['mean']:.3f}, std={v['std']:.3f}, min={v['min']:.3f}, max={v['max']:.3f}"
            )
        print(f"Viability Score: {self.viability_score():.2f}")
        print(f"Is Viable: {self.is_viable()}")


# Example usage:
# evaluator = WalkForwardEvaluator("c:/Users/ashou/AlgoRoyale/data/optimization/BollingerBandsStrategy/QUBT/20230101_20240101/optimization_result.json", metric_type="both")
# evaluator.print_report()
