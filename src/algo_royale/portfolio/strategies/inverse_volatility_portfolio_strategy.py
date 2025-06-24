import numpy as np
import pandas as pd
from optuna import Trial

from .base_portfolio_strategy import BasePortfolioStrategy


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
        weights = inv_vol.div(inv_vol.sum(axis=1), axis=0)
        weights = weights.fillna(0.0)
        return weights
