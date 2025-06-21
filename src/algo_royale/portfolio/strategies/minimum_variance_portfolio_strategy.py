import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from .base_portfolio_strategy import BasePortfolioStrategy


class MinimumVariancePortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates weights to minimize portfolio variance (risk) using historical returns.
    Uses a rolling window to estimate the covariance matrix.

    Example usage:
        strategy = MinimumVariancePortfolioStrategy(lookback=60)
        weights = strategy.allocate(signals, returns)

    Parameters:
        lookback: int, window size for covariance estimation (default: 60)
    """

    def __init__(self, lookback: int = 60):
        self.lookback = lookback

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(lookback=trial.suggest_int(f"{prefix}lookback", 10, 120))

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        weights = pd.DataFrame(
            index=signals.index, columns=signals.columns, dtype=float
        )
        for i in range(len(signals)):
            if i < self.lookback:
                weights.iloc[i] = np.nan
                continue
            window_returns = returns.iloc[i - self.lookback + 1 : i + 1]
            cov = window_returns.cov().values
            n = cov.shape[0]

            def obj(w):
                return w @ cov @ w

            cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
            bounds = [(0, 1)] * n
            res = minimize(obj, np.ones(n) / n, bounds=bounds, constraints=cons)
            if res.success:
                weights.iloc[i] = res.x
            else:
                weights.iloc[i] = np.nan
        weights = weights.fillna(0)
        return weights
