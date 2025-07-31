import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedWickReversalExitCondition(BaseBufferedCondition):
    """
    Buffered Wick Reversal Exit Condition
    Triggers when upper wick is sufficiently long compared to body.
    """

    def __init__(
        self,
        wick_body_ratio=2.0,
        upper_wick_col: SignalStrategyColumns = SignalStrategyColumns.UPPER_WICK,
        body_col: SignalStrategyColumns = SignalStrategyColumns.BODY,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.wick_body_ratio = wick_body_ratio
        self.upper_wick_col = upper_wick_col
        self.body_col = body_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.upper_wick_col, self.body_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        body_safe = df[self.body_col].iloc[-1]
        if body_safe == 0:
            body_safe = 1e-8
        long_upper_wick = (
            df[self.upper_wick_col].iloc[-1] > self.wick_body_ratio * body_safe
        )
        self.logger.debug(
            f"Upper wick: {df[self.upper_wick_col].iloc[-1]}, Body: {body_safe}, Ratio: {self.wick_body_ratio}, Result: {long_upper_wick}"
        )
        return long_upper_wick
