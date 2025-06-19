import json

import numpy as np


class WalkForwardEvaluator:
    def __init__(self, results_path):
        with open(results_path, "r") as f:
            self.results = json.load(f)
        self.metrics = self._extract_metrics()

    def _extract_metrics(self):
        metrics = []
        for window, data in self.results.items():
            # Prefer test metrics if available, else optimization
            if "test" in data and "metrics" in data["test"]:
                m = data["test"]["metrics"]
            elif "optimization" in data and "metrics" in data["optimization"]:
                m = data["optimization"]["metrics"]
            else:
                continue
            m["window"] = window
            metrics.append(m)
        return metrics

    def summary(self):
        df = {k: [m[k] for m in self.metrics] for k in self.metrics[0] if k != "window"}
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
        """
        Returns a score between 0 and 1 indicating overall viability.
        thresholds: dict with keys 'total_return', 'sharpe_ratio', 'win_rate', 'max_drawdown'
        """
        if thresholds is None:
            thresholds = {
                "total_return": 0.05,  # e.g., at least 5% mean return
                "sharpe_ratio": 0.5,  # e.g., at least 0.5 mean Sharpe
                "win_rate": 0.5,  # e.g., at least 50% mean win rate
                "max_drawdown": 0.5,  # e.g., max drawdown below 50%
            }
        summary = self.summary()
        score = 0
        checks = 0

        # Higher is better
        for metric in ["total_return", "sharpe_ratio", "win_rate"]:
            if metric in summary:
                checks += 1
                if summary[metric]["mean"] >= thresholds[metric]:
                    score += 1

        # Lower is better
        if "max_drawdown" in summary:
            checks += 1
            if summary["max_drawdown"]["mean"] <= thresholds["max_drawdown"]:
                score += 1

        return score / checks if checks > 0 else 0

    def is_viable(self, min_score=0.75):
        """Returns True if the strategy passes the viability threshold."""
        return self.viability_score() >= min_score

    def print_report(self):
        print("Walk-Forward Evaluation Report")
        print("=" * 32)
        for m in self.metrics:
            print(f"Window: {m['window']}")
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
# evaluator = WalkForwardEvaluator("c:/Users/ashou/AlgoRoyale/data/optimization/BollingerBandsStrategy/QUBT/optimization_result.json")
# evaluator.print_report()
