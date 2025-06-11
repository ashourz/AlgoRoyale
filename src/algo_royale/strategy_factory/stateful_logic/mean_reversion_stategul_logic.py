from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.enum.signal_type import SignalType

from .base_stateful_logic import StatefulLogic


class MeanReversionStatefulLogic(StatefulLogic):
    def __init__(
        self,
        window=20,
        threshold=0.02,
        stop_pct=0.02,
        profit_target_pct=0.04,
        reentry_cooldown=5,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(
            window=window,
            threshold=threshold,
            stop_pct=stop_pct,
            profit_target_pct=profit_target_pct,
            reentry_cooldown=reentry_cooldown,
            close_col=close_col,
        )
        self.window = window
        self.threshold = threshold
        self.stop_pct = stop_pct
        self.profit_target_pct = profit_target_pct
        self.reentry_cooldown = reentry_cooldown
        self.close_col = close_col

    def __call_impl(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
        if not state:
            state = {
                "in_position": False,
                "entry_price": None,
                "trailing_stop": None,
                "last_exit_idx": -self.reentry_cooldown,
            }
        price = df.iloc[i][self.close_col]
        ma = (
            df[self.close_col].rolling(window=self.window, min_periods=1).mean().iloc[i]
        )
        deviation = (price - ma) / ma

        if not state["in_position"]:
            if (i - state["last_exit_idx"]) > self.reentry_cooldown:
                if deviation < -self.threshold and trend_mask.iloc[i]:
                    signals.iloc[i] = SignalType.BUY.value
                    state["in_position"] = True
                    state["entry_price"] = price
                    state["trailing_stop"] = price * (1 - self.stop_pct)
        else:
            state["trailing_stop"] = max(
                state["trailing_stop"], price * (1 - self.stop_pct)
            )
            hit_stop = price < state["trailing_stop"]
            hit_profit = price >= state["entry_price"] * (1 + self.profit_target_pct)
            sell_signal = deviation > self.threshold or hit_stop or hit_profit

            if sell_signal:
                signals.iloc[i] = SignalType.SELL.value
                state["in_position"] = False
                state["entry_price"] = None
                state["trailing_stop"] = None
                state["last_exit_idx"] = i

        return signals.iloc[i], state

    @property
    def required_columns(self):
        """Override to specify required columns for mean reversion logic."""
        return {self.close_col}

    @classmethod
    def available_param_grid(cls) -> dict:
        """Override to provide parameter grid for mean reversion strategy."""
        return {
            "window": [5, 10, 15, 20, 25, 30, 40, 50],
            "threshold": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04],
            "stop_pct": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.35, 0.4, 0.45, 0.5],
            "profit_target_pct": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.35, 0.04],
            "reentry_cooldown": [0, 1, 2, 3, 5, 7, 10, 15, 20, 30],
            "close_col": [StrategyColumns.CLOSE_PRICE],
        }

    @classmethod
    def optuna_suggest(cls, trial, prefix=""):
        """Override to provide Optuna suggestions for mean reversion strategy."""
        window = trial.suggest_int(f"{prefix}window", 5, 50)
        threshold = trial.suggest_float(f"{prefix}threshold", 0.005, 0.04)
        stop_pct = trial.suggest_float(f"{prefix}stop_pct", 0.005, 0.5)
        profit_target_pct = trial.suggest_float(
            f"{prefix}profit_target_pct", 0.005, 0.04
        )
        reentry_cooldown = trial.suggest_int(f"{prefix}reentry_cooldown", 0, 30)
        close_col = StrategyColumns.CLOSE_PRICE
        return cls(
            window=window,
            threshold=threshold,
            stop_pct=stop_pct,
            profit_target_pct=profit_target_pct,
            reentry_cooldown=reentry_cooldown,
            close_col=close_col,
        )
