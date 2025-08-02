from algo_royale.backtester.strategy.signal.buffered_components.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_exit import (
    ComboExitCondition,
)


class BufferedComboExitCondition(BaseBufferedCondition):
    def __init__(self, *args, **kwargs):
        # You may want to set buffer_size based on the window required by ComboExitCondition
        super().__init__(*args, **kwargs)
        self.condition = ComboExitCondition(*args, **kwargs)

    def _evaluate_condition(self) -> bool:
        # Convert buffer to DataFrame if needed
        import pandas as pd

        if len(self.buffer) == 0:
            return False
        df = pd.DataFrame(self.buffer)
        # Use the last row for evaluation, or adapt as needed
        return self.condition._apply(df).iloc[-1]
