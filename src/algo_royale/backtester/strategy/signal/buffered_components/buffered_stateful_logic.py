from collections import deque

import pandas as pd

from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.logging.loggable import Loggable


class BufferedStatefulLogic:
    """
    Generic buffered wrapper for any stateful logic class that operates on a DataFrame window.
    Maintains its own buffer and applies the given stateful logic to the window.
    """

    def __init__(
        self,
        stateful_logic: StatefulLogic,
        window_size: int = 1,
        logger: Loggable = None,
    ):
        """
        :param stateful_logic: An instance of a stateful logic class with a __call__ method.
        :param window_size: The number of rows to buffer (window size).
        :param logger: Logger instance for logging (optional).
        """
        self.stateful_logic = stateful_logic
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self.logger = logger
        self.state = None  # Optionally maintain state between calls

    def update(
        self,
        row: dict,
        entry_signal=None,
        exit_signal=None,
        state=None,
        trend_mask=None,
        filter_mask=None,
    ):
        """
        Add a new row (dict or pd.Series) to the buffer and evaluate the stateful logic.
        Returns the result for the latest row in the window.
        """
        self.buffer.append(row)
        if len(self.buffer) < self.window_size:
            return None  # Not enough data yet
        df = pd.DataFrame(self.buffer)
        i = len(df) - 1  # Index of the latest row
        # Call the stateful logic's __call__ method
        result = self.stateful_logic(
            i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
        )
        return result
