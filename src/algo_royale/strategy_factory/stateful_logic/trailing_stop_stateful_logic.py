from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)


class TrailingStopStatefulLogic(StatefulLogic):
    """
    Implements a trailing stop as stateful logic.
    Keeps track of the highest price since entry and exits when price falls below trailing stop.
    """

    def __init__(self, close_col=StrategyColumns.CLOSE_PRICE, stop_pct=0.02):
        self.close_col = close_col
        self.stop_pct = stop_pct

    def __call__(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
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
                signal = "buy"
        else:
            # Update trailing high
            if price > state["trailing_high"]:
                state["trailing_high"] = price
            trailing_stop = state["trailing_high"] * (1 - self.stop_pct)
            if price < trailing_stop or (exit_mask is not None and exit_mask.iloc[i]):
                # Exit position
                state["in_position"] = False
                state["trailing_high"] = None
                signal = "sell"

        return signal, state

    @property
    def required_columns(self):
        return {self.close_col}

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE],
            "stop_pct": [0.01, 0.02, 0.03, 0.05],
        }
