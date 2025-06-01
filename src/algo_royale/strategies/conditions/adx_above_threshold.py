import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


@staticmethod
def adx_above_threshold(
    row,
    adx_col: StrategyColumns = StrategyColumns.ADX,
    close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    threshold=25,
):
    """
    Returns True if the ADX value is above a threshold (indicating strong trend).

    Args:
        row (pd.Series): A row of data.
        adx_col (StrategyColumns): Column name for the ADX values.
        close_col (StrategyColumns): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX > threshold, else False.
    """
    return row[adx_col] > threshold


class ADXAboveThresholdCondition(StrategyCondition):
    """Condition to check if ADX is above a specified threshold.
    This condition checks if the Average Directional Index (ADX) is above a specified threshold,
    indicating a strong trend in the market.
    This is typically used in trend-following strategies to filter out periods of low volatility.
    It is applied to each row of a DataFrame containing ADX values.
    This condition is useful for strategies that require a strong trend to enter trades.
    Args:
        adx_col (StrategyColumns): Column name for the ADX values.
        close_col (StrategyColumns): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        pd.Series: Boolean Series where True indicates ADX is above the threshold.

    Usage:
        filter = ADXAboveThresholdFilter(adx_col='ADX', close_col='Close', threshold=25)
        df['adx_above_threshold'] = filter.apply(df)
    """

    def __init__(
        self,
        adx_col: StrategyColumns = StrategyColumns.ADX,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        threshold: float = 25,
    ):
        self.adx_col = adx_col
        self.close_col = close_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: adx_above_threshold(
                row, self.adx_col, self.close_col, self.threshold
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.adx_col, self.close_col]
