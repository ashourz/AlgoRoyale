import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from .base_portfolio_strategy import BasePortfolioStrategy


class MeanVariancePortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates weights to maximize expected return for a given level of risk (mean-variance optimization).
    Uses rolling window for mean/covariance estimation.

    Example usage:
        strategy = MeanVariancePortfolioStrategy(lookback=60, risk_aversion=1.0)
        weights = strategy.allocate(signals, returns)

    Parameters:
        lookback: int, window size for mean/covariance estimation (default: 60)
        risk_aversion: float, risk aversion parameter (default: 1.0)
    """

    def __init__(self, lookback: int = 60, risk_aversion: float = 1.0):
        self.lookback = lookback
        self.risk_aversion = risk_aversion

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_aversion={self.risk_aversion})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_aversion={self.risk_aversion})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            lookback=trial.suggest_int(f"{prefix}lookback", 10, 120),
            risk_aversion=trial.suggest_float(
                f"{prefix}risk_aversion", 0.01, 10.0, log=True
            ),
        )

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        if returns.empty or returns.shape[1] == 0:
            return pd.DataFrame(index=returns.index)
        if returns.shape[1] == 1:
            # Only one asset: allocate 100% to it
            weights = pd.DataFrame(1.0, index=returns.index, columns=returns.columns)
            return weights
        weights = pd.DataFrame(
            index=signals.index, columns=signals.columns, dtype=float
        )
        for i in range(len(signals)):
            if i < self.lookback:
                weights.iloc[i] = np.nan
                continue
            window_returns = returns.iloc[i - self.lookback + 1 : i + 1]
            mu = window_returns.mean().values
            cov = window_returns.cov().values
            n = len(mu)
            if n == 1:
                weights.iloc[i] = 1.0
                continue

            def obj(w):
                return -w @ mu + self.risk_aversion * w @ cov @ w

            cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
            bounds = [(0, 1)] * n
            res = minimize(obj, np.ones(n) / n, bounds=bounds, constraints=cons)
            if res.success:
                weights.iloc[i] = res.x
            else:
                weights.iloc[i] = np.nan
        weights = weights.fillna(0)
        return weights
