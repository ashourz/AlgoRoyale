from typing import Any, Dict

import pandas as pd


class PortfolioBacktestExecutor:
    """
    Executes a portfolio strategy over a DataFrame of returns/signals and produces portfolio results.
    """

    def run_backtest(self, strategy, data: pd.DataFrame) -> Dict[str, Any]:
        # Example: call strategy.allocate and compute portfolio returns
        weights = strategy.allocate(data, data)  # or (signals, returns) as needed
        portfolio_returns = (weights * data).sum(axis=1)
        results = {
            "weights": weights,
            "portfolio_returns": portfolio_returns,
        }
        return results
