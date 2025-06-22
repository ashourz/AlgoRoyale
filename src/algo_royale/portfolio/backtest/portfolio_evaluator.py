from typing import Any, Dict

import pandas as pd


class PortfolioEvaluator:
    """
    Evaluates portfolio backtest results and computes performance metrics.
    """

    def evaluate(self, strategy, results: Dict[str, Any]) -> Dict[str, Any]:
        returns = results["portfolio_returns"]
        metrics = {
            "total_return": float(returns.sum()),
            "mean_return": float(returns.mean()),
            "volatility": float(returns.std()),
            "sharpe_ratio": float(returns.mean() / (returns.std() + 1e-8)),
            "max_drawdown": float(self.max_drawdown(returns)),
        }
        return metrics

    @staticmethod
    def max_drawdown(returns: pd.Series) -> float:
        cum_returns = (1 + returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return drawdown.min()
