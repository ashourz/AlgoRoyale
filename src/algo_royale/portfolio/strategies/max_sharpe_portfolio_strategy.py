import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from .base_portfolio_strategy import BasePortfolioStrategy


class MaxSharpePortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates weights to maximize the Sharpe ratio (risk-adjusted return).
    Uses rolling window for mean/covariance estimation.

    Example usage:
        strategy = MaxSharpePortfolioStrategy(lookback=60, risk_free_rate=0.0)
        weights = strategy.allocate(signals, returns)

    Parameters:
        lookback: int, window size for mean/covariance estimation (default: 60)
        risk_free_rate: float, risk-free rate for Sharpe ratio calculation (default: 0.0)
    """

    def __init__(self, lookback: int = 60, risk_free_rate: float = 0.0):
        self.lookback = lookback
        self.risk_free_rate = risk_free_rate

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_free_rate={self.risk_free_rate})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_free_rate={self.risk_free_rate})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            lookback=trial.suggest_int(f"{prefix}lookback", 10, 120),
            risk_free_rate=trial.suggest_float(f"{prefix}risk_free_rate", 0.0, 0.05),
        )

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
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

            def neg_sharpe(w):
                port_ret = w @ mu
                port_vol = np.sqrt(w @ cov @ w)
                return -(port_ret - self.risk_free_rate) / (port_vol + 1e-8)

            cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
            bounds = [(0, 1)] * n
            res = minimize(neg_sharpe, np.ones(n) / n, bounds=bounds, constraints=cons)
            if res.success:
                weights.iloc[i] = res.x
            else:
                weights.iloc[i] = np.nan
        weights = weights.fillna(0)
        return weights
