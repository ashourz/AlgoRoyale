import numpy as np
import pandas as pd
from optuna import Trial

from .base_portfolio_strategy import BasePortfolioStrategy


class RiskParityPortfolioStrategy(BasePortfolioStrategy):
    """Portfolio strategy that allocates weights so each asset contributes equally to portfolio risk.
    Uses rolling window covariance estimation and an iterative risk parity solver.

    Example usage:
        strategy = RiskParityPortfolioStrategy(window=20, max_iter=100, tol=1e-6)
        weights = strategy.allocate(signals, returns)

    Parameters:
        window: int, rolling window size for covariance estimation (default: 20)
        max_iter: int, maximum iterations for risk parity solver (default: 100)
        tol: float, tolerance for convergence (default: 1e-6)
    """

    def __init__(self, window: int = 20, max_iter: int = 100, tol: float = 1e-6):
        self.window = window
        self.max_iter = max_iter
        self.tol = tol

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(window={self.window}, max_iter={self.max_iter}, tol={self.tol})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(window={self.window}, max_iter={self.max_iter}, tol={self.tol})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            window=trial.suggest_int(f"{prefix}window", 5, 60),
            max_iter=trial.suggest_int(f"{prefix}max_iter", 50, 500),
            tol=trial.suggest_float(f"{prefix}tol", 1e-8, 1e-3, log=True),
        )

    def _risk_parity_weights(self, cov):
        n = cov.shape[0]
        w = np.ones(n) / n
        for _ in range(self.max_iter):
            risk_contrib = w * (cov @ w)
            avg_rc = risk_contrib.mean()
            diff = risk_contrib - avg_rc
            if np.abs(diff).max() < self.tol:
                break
            w -= 0.01 * diff
            w = np.clip(w, 1e-6, 1)
            w /= w.sum()
        return w

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Allocate weights so each asset has equal risk contribution.
        Parameters:
            signals: DataFrame of signals (index: datetime, columns: symbols)
            returns: DataFrame of returns (index: datetime, columns: symbols)
        Returns:
            DataFrame of weights (index: datetime, columns: symbols)
        """
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
            if i < self.window:
                weights.iloc[i] = np.nan
                continue
            window_returns = returns.iloc[i - self.window + 1 : i + 1]
            cov = window_returns.cov().values
            if cov.shape[0] == 1:
                weights.iloc[i] = 1.0
                continue
            w = self._risk_parity_weights(cov)
            weights.iloc[i] = w
        weights = weights.fillna(0)
        return weights
