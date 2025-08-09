import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


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

    def __init__(
        self, logger: Loggable, lookback: int = 60, risk_aversion: float = 1.0
    ):
        self.lookback = lookback
        self.risk_aversion = risk_aversion
        super().__init__(logger=logger)

    @property
    def required_columns(self):
        return set()

    @property
    def window_size(self) -> int:
        """Override in subclasses to specify the window size for buffered portfolio strategies."""
        return self.lookback

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_aversion={self.risk_aversion})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(lookback={self.lookback}, risk_aversion={self.risk_aversion})"

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        return cls(
            logger=logger,
            lookback=trial.suggest_int(f"{prefix}lookback", 10, 120),
            risk_aversion=trial.suggest_float(
                f"{prefix}risk_aversion", 0.01, 10.0, log=True
            ),
        )

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
            mu = window_returns.mean().values
            cov = window_returns.cov().values
            n = len(mu)
            if n == 1:
                weights.iloc[i] = 1.0
                continue

            def obj(w):
                if np.any(~np.isfinite(w)):
                    return np.inf
                var = w @ cov @ w
                if np.isnan(var) or not np.isfinite(var) or var < 0:
                    return np.inf
                result = -w @ mu + self.risk_aversion * var
                if np.isnan(result) or not np.isfinite(result):
                    return np.inf
                return result

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
