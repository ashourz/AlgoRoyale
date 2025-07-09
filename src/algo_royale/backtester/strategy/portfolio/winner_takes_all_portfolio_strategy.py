import pandas as pd
from optuna import Trial

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class WinnerTakesAllPortfolioStrategy(BasePortfolioStrategy):
    """
    Portfolio strategy that allocates 100% of capital to the asset with the highest signal (or return) at each time step.
    Optionally, moves to cash at the end of each day (or time step) if desired.

    Example usage:
        strategy = WinnerTakesAllPortfolioStrategy(use_signals=True, move_to_cash_at_end_of_day=True)
        weights = strategy.allocate(signals, returns)

    Parameters:
        use_signals: bool, if True use signals DataFrame, else use returns DataFrame to pick the winner (default: True)
        move_to_cash_at_end_of_day: bool, if True, sets all weights to zero at the end of each day (default: False)
    """

    def __init__(
        self, use_signals: bool = True, move_to_cash_at_end_of_day: bool = False
    ):
        self.use_signals = use_signals
        self.move_to_cash_at_end_of_day = move_to_cash_at_end_of_day

    @property
    def required_columns(self):
        return set()

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(use_signals={self.use_signals}, move_to_cash_at_end_of_day={self.move_to_cash_at_end_of_day})"

    def get_id(self) -> str:
        return f"{self.__class__.__name__}(use_signals={self.use_signals}, move_to_cash_at_end_of_day={self.move_to_cash_at_end_of_day})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            use_signals=trial.suggest_categorical(
                f"{prefix}use_signals", [True, False]
            ),
            move_to_cash_at_end_of_day=trial.suggest_categorical(
                f"{prefix}move_to_cash_at_end_of_day", [True, False]
            ),
        )

    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        # --- Ensure all values are numeric before any math ---
        signals = signals.apply(pd.to_numeric, errors="coerce")
        returns = returns.apply(pd.to_numeric, errors="coerce")
        # Do not fillna here; let NaN propagate if math cannot be performed

        data = signals if self.use_signals else returns
        if data.empty or data.shape[1] == 0:
            return pd.DataFrame(index=data.index)
        if data.shape[1] == 1:
            # Only one asset: allocate 100% if value is positive, else 0
            col = data.columns[0]
            weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)
            weights[col] = data[col].apply(
                lambda x: 1.0 if pd.notnull(x) and x > 0 else 0.0
            )
            return weights
        weights = pd.DataFrame(0, index=data.index, columns=data.columns, dtype=float)
        for i, row in data.iterrows():
            if row.isnull().all():
                continue
            winner = row.idxmax()
            if pd.notnull(row[winner]) and row[winner] > 0:
                weights.loc[i, winner] = 1.0
        if self.move_to_cash_at_end_of_day:
            weights.iloc[-1] = 0.0  # Move to cash at the last time step (end of day)
        # Normalize weights to sum to 1, handle NaN/inf
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
