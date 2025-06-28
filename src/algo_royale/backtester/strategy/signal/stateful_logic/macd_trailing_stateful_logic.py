import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.enum.signal_type import SignalType
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)


class MACDTrailingStatefulLogic(StatefulLogic):
    """
    Implements a MACD-based trading strategy with a trailing stop loss.
    This strategy generates buy and sell signals based on MACD crossovers
    and maintains a trailing stop loss to protect profits.

    Parameters:
        close_col (StrategyColumns): Column to use for closing prices.
        fast (int): Fast EMA period for MACD.
        slow (int): Slow EMA period for MACD.
        signal (int): Signal line period for MACD.
        stop_pct (float): Percentage for trailing stop loss.
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        stop_pct: float = 0.02,
    ):
        super().__init__(
            close_col=close_col,
            fast=fast,
            slow=slow,
            signal=signal,
            stop_pct=stop_pct,
        )
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.stop_pct = stop_pct

    def __call_impl(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
        # Initialize state if empty
        if not state:
            state = {
                "in_position": False,
                "trailing_stop": None,
            }

        exp1 = df[self.close_col].ewm(span=self.fast, adjust=False).mean()
        exp2 = df[self.close_col].ewm(span=self.slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()
        macd_prev = macd.shift(1)
        signal_prev = signal_line.shift(1)

        # Skip if not enough data
        if pd.isna(macd.iloc[i]) or pd.isna(signal_line.iloc[i]):
            return signals.iloc[i], state

        price = df.iloc[i][self.close_col]
        trend_ok = trend_mask.iloc[i]

        if not state["in_position"]:
            buy_signal = (macd_prev.iloc[i] < signal_prev.iloc[i]) and (
                macd.iloc[i] > signal_line.iloc[i]
            )
            if buy_signal and trend_ok:
                signals.iloc[i] = SignalType.BUY.value
                state["in_position"] = True
                state["trailing_stop"] = price * (1 - self.stop_pct)
        else:
            state["trailing_stop"] = max(
                state["trailing_stop"], price * (1 - self.stop_pct)
            )
            sell_signal = (macd_prev.iloc[i] > signal_prev.iloc[i]) and (
                macd.iloc[i] < signal_line.iloc[i]
            )
            if sell_signal or price < state["trailing_stop"]:
                signals.iloc[i] = SignalType.SELL.value
                state["in_position"] = False
                state["trailing_stop"] = None

        return signals.iloc[i], state

    @property
    def required_columns(self):
        """
        Returns a list of required columns for this stateful logic.
        """
        return [self.close_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        """
        Returns a dict of parameter names to lists of possible values.
        This allows for hyperparameter tuning.
        """
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "fast": [8, 10, 12, 14, 16],
            "slow": [20, 22, 24, 26, 28, 30, 32],
            "signal": [7, 9, 10, 11, 13],
            "stop_pct": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.35, 0.4, 0.45, 0.5],
        }

    @classmethod
    def optuna_suggest(cls, trial, prefix=""):
        """
        Suggests hyperparameters for this stateful logic using Optuna.
        """
        close_col = trial.suggest_categorical(
            f"{prefix}close_col",
            [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
        )
        fast = trial.suggest_int(f"{prefix}fast", 8, 16)
        slow = trial.suggest_int(f"{prefix}slow", 20, 32)
        signal = trial.suggest_int(f"{prefix}signal", 7, 13)
        stop_pct = trial.suggest_float(f"{prefix}stop_pct", 0.005, 0.5)

        return cls(
            close_col=close_col,
            fast=fast,
            slow=slow,
            signal=signal,
            stop_pct=stop_pct,
        )
