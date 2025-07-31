import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedVWAPReversionEntryCondition(BaseBufferedCondition):
    """
    Buffered VWAP Reversion Entry Condition
    Triggers when price deviates below VWAP by a threshold.
    """

    def __init__(
        self,
        deviation_threshold=0.01,
        vwap_col: SignalStrategyColumns = SignalStrategyColumns.VWAP_20,
        vwp_col: SignalStrategyColumns = SignalStrategyColumns.VOLUME_WEIGHTED_PRICE,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.vwap_col, self.vwp_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        deviation = (df[self.vwp_col].iloc[-1] - df[self.vwap_col].iloc[-1]) / df[
            self.vwap_col
        ].iloc[-1]
        result = deviation < -self.deviation_threshold
        self.logger.debug(
            f"Deviation: {deviation}, Threshold: {self.deviation_threshold}, Result: {result}"
        )
        return result
