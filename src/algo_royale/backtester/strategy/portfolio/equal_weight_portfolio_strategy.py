import pandas as pd
from optuna import Trial

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class EqualWeightPortfolioStrategy(BasePortfolioStrategy):
    """Portfolio strategy that allocates equal weights to all available symbols at each time step.
    This strategy does not consider any signals or returns, simply distributing weights evenly.
    It is useful as a baseline for comparison against more complex strategies.

    Example usage:
        strategy = EqualWeightPortfolioStrategy()
        weights = strategy.allocate(signals, returns)

    Example input:
        signals = pd.DataFrame({
            'AAPL': [1, 0, 1],
            'GOOGL': [0, 1, 1],
            'MSFT': [1, 1, 0]
        }, index=pd.date_range('2023-01-01', periods=3))

        returns = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.03],
            'GOOGL': [-0.01, 0.02, 0.01],
            'MSFT': [0.02, -0.01, 0.02]
        }, index=pd.date_range('2023-01-01', periods=3))

    Example output:
        weights = pd.DataFrame({
            'AAPL': [0.333, 0.333, 0.333],
            'GOOGL': [0.333, 0.333, 0.333],
            'MSFT': [0.333, 0.333, 0.333]
        }, index=pd.date_range('2023-01-01', periods=3))
    """

    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}()"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}()"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls()

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Given signals and/or returns, produce a DataFrame of portfolio weights over time.
        Parameters:
            signals: DataFrame of signals (index: datetime, columns: symbols)
            returns: DataFrame of returns (index: datetime, columns: symbols)
        Returns:
            DataFrame of weights (index: datetime, columns: symbols)
        """
        # --- Ensure all values are numeric before any math ---
        signals = signals.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        returns = returns.apply(pd.to_numeric, errors="coerce").fillna(0.0)

        if signals.empty or signals.shape[1] == 0:
            # No assets to allocate
            return pd.DataFrame(index=signals.index)
        n_assets = signals.shape[1]
        if n_assets == 1:
            # Only one asset: allocate 100% to it
            weights = pd.DataFrame(1.0, index=signals.index, columns=signals.columns)
            return weights
        # Check for all-NaN columns
        if signals.isnull().all().all():
            return pd.DataFrame(0.0, index=signals.index, columns=signals.columns)
        weights = pd.DataFrame(
            1.0 / n_assets, index=signals.index, columns=signals.columns
        )
        # --- Robust normalization and error handling ---
        import numpy as np

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
