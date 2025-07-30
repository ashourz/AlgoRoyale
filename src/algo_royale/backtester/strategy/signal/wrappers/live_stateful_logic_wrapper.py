from collections import deque

import pandas as pd

from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)


class LiveStatefulLogicWrapper:
    def __init__(self, stateful_logic: StatefulLogic, window: int = 1):
        self.stateful_logic = stateful_logic
        self.window = window
        self.buffer = deque(maxlen=window)

    def __call__(
        self, df, entry_signal, exit_signal, state, trend_mask, filter_mask
    ) -> pd.Series:
        """
        Dual-signal interface for live stateful logic.
        """
        self.buffer.append(df.iloc[0])
        df = pd.DataFrame(list(self.buffer))
        i = len(self.buffer) - 1  # Index of the latest row
        result_series = self.stateful_logic(
            i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
        )
        return result_series.iloc[-1] if not result_series.empty else None
