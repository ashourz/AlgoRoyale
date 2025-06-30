import numpy as np
import pandas as pd
from optuna import Trial

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class MomentumPortfolioStrategy(BasePortfolioStrategy):
    """Portfolio strategy that allocates more weight to assets with higher recent momentum.
    Momentum is measured as cumulative return over a rolling window.

    Example usage:
        strategy = MomentumPortfolioStrategy(window=20)
        weights = strategy.allocate(signals, returns)

    Parameters:
        window: int, rolling window size for momentum estimation (default: 20)
    """

    def __init__(self, window: int = 20):
        self.window = window

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(window={self.window})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(window={self.window})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(window=trial.suggest_int(f"{prefix}window", 5, 60))

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Allocate weights proportional to positive momentum.
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
        momentum = (1 + returns).rolling(self.window, min_periods=1).apply(
            np.prod, raw=True
        ) - 1
        momentum = momentum.clip(lower=0.0)
        weights = momentum.div(momentum.sum(axis=1), axis=0)
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
