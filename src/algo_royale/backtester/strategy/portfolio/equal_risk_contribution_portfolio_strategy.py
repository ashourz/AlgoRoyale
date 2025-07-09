import numpy as np
import pandas as pd
from optuna import Trial
from scipy.optimize import minimize

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class EqualRiskContributionPortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates weights so each asset contributes equally to portfolio risk (equal risk contribution).
    Uses rolling window for covariance estimation.

    Example usage:
        strategy = EqualRiskContributionPortfolioStrategy(lookback=60)
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

            def risk_contribution(w):
                port_var = w @ cov @ w
                if port_var <= 0 or np.isnan(port_var):
                    return np.inf  # Penalize invalid variance
                rc = w * (cov @ w) / (np.sqrt(port_var) + 1e-8)
                return np.sum((rc - rc.mean()) ** 2)

            cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
            bounds = [(0, 1)] * n
            res = minimize(
                risk_contribution, np.ones(n) / n, bounds=bounds, constraints=cons
            )
            if res.success:
                weights.iloc[i] = res.x
            else:
                weights.iloc[i] = np.nan
        # --- Robust normalization and error handling ---
        weights = weights.replace([np.inf, -np.inf], 0.0).fillna(0.0)
        # Mask and normalize using latest available prices
        if not returns.empty:
            latest_prices = returns.iloc[
                -1
            ].abs()  # Use abs() in case returns are used as proxy for prices
            weights = self._mask_and_normalize_weights(
                weights,
                pd.DataFrame(
                    [latest_prices] * len(weights),
                    index=weights.index,
                    columns=weights.columns,
                ),
            )
        row_sums = weights.sum(axis=1)
        for idx, s in row_sums.items():
            if np.isclose(s, 0.0):
                weights.loc[idx] = 0.0
            else:
                weights.loc[idx] = weights.loc[idx] / s
        abnormal = row_sums[(row_sums < 0.99) | (row_sums > 1.01)]
        if not abnormal.empty:
            import logging

            logging.warning(
                f"EqualRiskContributionPortfolioStrategy: Abnormal weight row sums at: {abnormal.index.tolist()} values: {abnormal.values}"
            )
        return weights
