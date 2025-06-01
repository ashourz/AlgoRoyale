import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class MovingAverageCrossoverExitCondition(StrategyCondition):
    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        short_window=10,
        long_window=50,
        trend_window=200,
        volume_ma_window=20,
        ma_type="ema",
    ):
        self.close_col = close_col
        self.volume_col = volume_col
        self.short_window = short_window
        self.long_window = long_window
        self.trend_window = trend_window
        self.volume_ma_window = volume_ma_window
        self.ma_type = ma_type

    @property
    def required_columns(self):
        cols = [self.close_col]
        if self.volume_col:
            cols.append(self.volume_col)
        return set(cols)

    def _moving_average(self, series: pd.Series, window: int) -> pd.Series:
        if self.ma_type == "ema":
            return series.ewm(span=window, adjust=False).mean()
        else:
            return series.rolling(window=window, min_periods=window).mean()

    def apply(self, df: pd.DataFrame) -> pd.Series:
        short_ma = self._moving_average(df[self.close_col], self.short_window)
        long_ma = self._moving_average(df[self.close_col], self.long_window)
        trend_ma = self._moving_average(df[self.close_col], self.trend_window)

        if self.volume_col and self.volume_col in df.columns:
            vol_ma = (
                df[self.volume_col]
                .rolling(window=self.volume_ma_window, min_periods=1)
                .mean()
            )
            volume_condition = df[self.volume_col] > vol_ma
        else:
            volume_condition = pd.Series(True, index=df.index)

        crossover_signal = pd.Series(0, index=df.index)
        crossover_signal[short_ma > long_ma] = 1
        crossover_signal[short_ma < long_ma] = -1

        sell_condition = (
            (crossover_signal == -1)
            & (crossover_signal.shift(1) != -1)
            & (df[self.close_col] < trend_ma)
            & volume_condition
        )
        return sell_condition
