from collections import deque

import pandas as pd

from algo_royale.logging.loggable import Loggable


class GenericBufferedCondition:
    """
    Generic buffered condition wrapper for any condition class that operates on a DataFrame window.
    Maintains its own buffer and applies the given condition to the window.
    """

    def __init__(self, condition, window_size=1, logger: Loggable = None):
        """
        :param condition: An instance of a condition class with an _apply(df) method.
        :param window_size: The number of rows to buffer (window size).
        :param logger: Logger instance for logging.
        """
        self.condition = condition
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self.logger = logger

    def update(self, row: dict):
        """
        Add a new row (dict or pd.Series) to the buffer and evaluate the condition.
        Returns the condition result for the latest row in the window.
        """
        self.buffer.append(row)
        if not self.buffer:
            return False
        if len(self.buffer) < self.window_size:
            return False  # Not enough data yet
        if len(self.buffer) > self.window_size:
            self.buffer.pop()
        df = pd.DataFrame(self.buffer)
        # Assumes the condition's _apply returns a Series
        return self.condition._apply(df).iloc[-1]
