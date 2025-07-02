from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enum.signal_type import SignalType
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)


class TrailingStopStatefulLogic(StatefulLogic):
    """
    Implements a trailing stop as stateful logic.
    Keeps track of the highest price since entry and exits when price falls below trailing stop.
    """

    def __init__(self, close_col=SignalStrategyColumns.CLOSE_PRICE, stop_pct=0.02):
        super().__init__(close_col=close_col, stop_pct=stop_pct)
        self.close_col = close_col
        self.stop_pct = stop_pct

    def __call_impl(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
        # Initialize state if needed
        if state is None or "trailing_high" not in state:
            state = {"in_position": False, "trailing_high": None}

        price = df.iloc[i][self.close_col]
        signal = signals.iloc[i]

        if not state["in_position"]:
            if entry_mask.iloc[i]:
                # Enter position
                state["in_position"] = True
                state["trailing_high"] = price
                signal = SignalType.BUY.value
        else:
            # Update trailing high
            if price > state["trailing_high"]:
                state["trailing_high"] = price
            trailing_stop = state["trailing_high"] * (1 - self.stop_pct)
            if price < trailing_stop or (exit_mask is not None and exit_mask.iloc[i]):
                # Exit position
                state["in_position"] = False
                state["trailing_high"] = None
                signal = SignalType.SELL.value

        return signal, state

    @property
    def required_columns(self):
        return [self.close_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [SignalStrategyColumns.CLOSE_PRICE],
            "stop_pct": [0.01, 0.02, 0.03, 0.05],
        }

    @classmethod
    def optuna_suggest(cls, trial, prefix: str = ""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col", [SignalStrategyColumns.CLOSE_PRICE]
            ),
            stop_pct=trial.suggest_float(f"{prefix}stop_pct", 0.01, 0.05),
        )
