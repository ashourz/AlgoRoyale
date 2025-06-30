import numpy as np
import pandas as pd
from optuna import Trial

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class InverseVolatilityPortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates weights inversely proportional to asset volatility (classic inverse volatility weighting).
    Lower volatility assets receive higher weights.

    Example usage:
        strategy = InverseVolatilityPortfolioStrategy(lookback=20)
        weights = strategy.allocate(signals, returns)

    Parameters:
        lookback: int, rolling window size for volatility estimation (default: 20)
    """

    def __init__(self, lookback: int = 20):
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
        return cls(lookback=trial.suggest_int(f"{prefix}lookback", 5, 60))

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        if returns.empty or returns.shape[1] == 0:
            return pd.DataFrame(index=returns.index)
        if returns.shape[1] == 1:
            # Only one asset: allocate 100% to it
            weights = pd.DataFrame(1.0, index=returns.index, columns=returns.columns)
            return weights
        rolling_vol = returns.rolling(self.lookback, min_periods=1).std()
        inv_vol = 1.0 / (rolling_vol + 1e-8)
        inv_vol = inv_vol.replace([np.inf, -np.inf], 0.0)
        row_sums = inv_vol.sum(axis=1)
        zero_sum_mask = row_sums == 0.0
        if zero_sum_mask.any():
            import logging

            logging.warning(
                f"InverseVolatilityPortfolioStrategy: Zero or NaN volatility row(s) detected at index: {returns.index[zero_sum_mask].tolist()}. Setting weights to zero for these rows."
            )
            inv_vol.loc[zero_sum_mask, :] = 0.0
            row_sums[zero_sum_mask] = 1.0  # Prevent division by zero
        weights = inv_vol.div(row_sums, axis=0)
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
