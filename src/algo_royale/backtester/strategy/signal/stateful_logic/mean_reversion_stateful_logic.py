from typing import Optional

from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.logging.loggable import Loggable


class MeanReversionStatefulLogic(StatefulLogic):
    def __init__(
        self,
        logger: Optional[Loggable] = None,
        window=20,
        threshold=0.02,
        stop_pct=0.02,
        profit_target_pct=0.04,
        reentry_cooldown=5,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(
            window=window,
            threshold=threshold,
            stop_pct=stop_pct,
            profit_target_pct=profit_target_pct,
            reentry_cooldown=reentry_cooldown,
            close_col=close_col,
            logger=logger,
        )
        self.window = window
        self.threshold = threshold
        self.stop_pct = stop_pct
        self.profit_target_pct = profit_target_pct
        self.reentry_cooldown = reentry_cooldown
        self.close_col = close_col

    def _call_impl(
        self, i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
    ):
        if self.logger:
            self.logger.debug(f"Processing index {i} with state: {state}")
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

        new_entry_signal = entry_signal
        new_exit_signal = exit_signal

        if not state["in_position"]:
            if (i - state["last_exit_idx"]) > self.reentry_cooldown:
                if deviation < -self.threshold and trend_mask.iloc[i]:
                    if self.logger:
                        self.logger.debug(
                            f"Buy signal at index {i}: price={price}, ma={ma}, deviation={deviation}"
                        )
                    new_entry_signal = SignalType.BUY.value
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
                if self.logger:
                    self.logger.debug(
                        f"Sell signal at index {i}: price={price}, entry_price={state['entry_price']}, "
                        f"trailing_stop={state['trailing_stop']}, deviation={deviation}"
                    )
                new_exit_signal = SignalType.SELL.value
                state["in_position"] = False
                state["entry_price"] = None
                state["trailing_stop"] = None
                state["last_exit_idx"] = i

        return new_entry_signal, new_exit_signal, state

    @property
    def required_columns(self):
        """Override to specify required columns for mean reversion logic."""
        return {self.close_col}

    @property
    def window_size(self) -> int:
        """Override to specify the window size for mean reversion logic."""
        return self.window

    @classmethod
    def available_param_grid(cls) -> dict:
        """Override to provide parameter grid for mean reversion strategy."""
        return {
            "window": [5, 10, 15, 20, 25, 30, 40, 50],
            "threshold": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04],
            "stop_pct": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.35, 0.4, 0.45, 0.5],
            "profit_target_pct": [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.35, 0.04],
            "reentry_cooldown": [0, 1, 2, 3, 5, 7, 10, 15, 20, 30],
            "close_col": [SignalStrategyColumns.CLOSE_PRICE],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        """Override to provide Optuna suggestions for mean reversion strategy."""
        window = trial.suggest_int(f"{prefix}window", 5, 50)
        threshold = trial.suggest_float(f"{prefix}threshold", 0.005, 0.04)
        stop_pct = trial.suggest_float(f"{prefix}stop_pct", 0.005, 0.5)
        profit_target_pct = trial.suggest_float(
            f"{prefix}profit_target_pct", 0.005, 0.04
        )
        reentry_cooldown = trial.suggest_int(f"{prefix}reentry_cooldown", 0, 30)
        close_col = SignalStrategyColumns.CLOSE_PRICE
        return cls(
            logger=logger,
            window=window,
            threshold=threshold,
            stop_pct=stop_pct,
            profit_target_pct=profit_target_pct,
            reentry_cooldown=reentry_cooldown,
            close_col=close_col,
        )
