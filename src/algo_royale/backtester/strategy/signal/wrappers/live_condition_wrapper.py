from collections import deque

import pandas as pd

from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class LiveConditionWrapper:
    def __init__(self, condition: StrategyCondition, window: int = 1):
        self.condition = condition
        self.window = window
        self.buffer = deque(maxlen=window)

    def
