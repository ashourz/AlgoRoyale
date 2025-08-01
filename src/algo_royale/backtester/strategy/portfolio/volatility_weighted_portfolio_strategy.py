import numpy as np
import pandas as pd
from optuna import Trial

from algo_royale.logging.loggable import Loggable
from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class VolatilityWeightedPortfolioStrategy(BasePortfolioStrategy):
    """Portfolio strategy that allocates weights inversely proportional to asset volatility.
    Lower volatility assets receive higher weights.

    Example usage:
        strategy = VolatilityWeightedPortfolioStrategy(window=20)
        weights = strategy.allocate(signals, returns)

    Parameters:
        window: int, rolling window size for volatility estimation (default: 20)
    """

    def __init__(self, logger: Loggable, window: int = 20):
        self.window = window
        super().__init__(logger=logger)

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(window={self.window})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(window={self.window})"

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        return cls(logger=logger, window=trial.suggest_int(f"{prefix}window", 5, 60))

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        # --- Ensure all values are numeric before any math ---
        signals = signals.apply(pd.to_numeric, errors="coerce")
        returns = returns.apply(pd.to_numeric, errors="coerce")
        # Do not fillna here; let NaN propagate if math cannot be performed

        """
        Allocate weights inversely to rolling volatility.
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
        rolling_vol = returns.rolling(self.window, min_periods=1).std()
        inv_vol = 1.0 / (rolling_vol + 1e-8)
        inv_vol = inv_vol.replace([np.inf, -np.inf], 0.0)
        weights = inv_vol.div(inv_vol.sum(axis=1), axis=0)
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
        # --- Robust normalization and error handling ---
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
                f"VolatilityWeightedPortfolioStrategy: Abnormal weight row sums at: {abnormal.index.tolist()} values: {abnormal.values}"
            )
        return weights
