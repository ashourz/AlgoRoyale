import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


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

    def __init__(self, lookback: int = 60, debug: bool = False):
        self.lookback = lookback
        super().__init__(debug=debug)

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
        # --- Ensure all values are numeric before any math ---
        signals = signals.apply(pd.to_numeric, errors="coerce")
        returns = returns.apply(pd.to_numeric, errors="coerce")
        # Do not fillna here; let NaN propagate if math cannot be performed

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
            cov = window_returns.cov().values
            n = cov.shape[0]
            if n == 1:
                weights.iloc[i] = 1.0
                continue

            def obj(w):
                if np.any(~np.isfinite(w)):
                    return np.inf
                var = w @ cov @ w
                if np.isnan(var) or not np.isfinite(var) or var < 0:
                    return np.inf
                return var

            cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
            bounds = [(0, 1)] * n
            res = minimize(obj, np.ones(n) / n, bounds=bounds, constraints=cons)
            if res.success:
                weights.iloc[i] = res.x
            else:
                weights.iloc[i] = np.nan
        weights = weights.fillna(0)
        weights = weights.replace([np.inf, -np.inf], 0.0).fillna(0.0)
        if not returns.empty:
            latest_prices = returns.iloc[-1].abs()
            weights = self._mask_and_normalize_weights(
                weights,
                pd.DataFrame(
                    [latest_prices] * len(weights),
                    index=weights.index,
                    columns=weights.columns,
                ),
            )
        return weights
