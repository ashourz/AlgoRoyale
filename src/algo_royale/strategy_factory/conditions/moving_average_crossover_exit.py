import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.strategy_factory.enum.ma_type import MA_Type


class MovingAverageCrossoverExitCondition(StrategyCondition):
    """
    Condition to check for a moving average crossover exit signal.
    This condition checks if the short-term moving average crosses below the long-term moving average,
    indicating a potential bearish trend. It also checks if the price is below a longer-term trend moving average
    and if the volume is below its moving average, which can confirm the strength of the signal.
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        short_window: int = 10,
        long_window: int = 50,
        trend_window: int = 200,
        volume_ma_window=20,
        ma_type: MA_Type = MA_Type.EMA,
    ):
        super().__init__(
            close_col=close_col,
            volume_col=volume_col,
            short_window=short_window,
            long_window=long_window,
            trend_window=trend_window,
            volume_ma_window=volume_ma_window,
            ma_type=ma_type,
        )
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
        if self.ma_type == MA_Type.EMA:
            return series.ewm(span=window, adjust=False).mean()
        else:
            return series.rolling(window=window, min_periods=window).mean()

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        short_ma = self._moving_average(df[self.close_col], self.short_window)
        long_ma = self._moving_average(df[self.close_col], self.long_window)
        trend_ma = self._moving_average(df[self.close_col], self.trend_window)

        if self.volume_col and self.volume_col in df.columns:
            vol_ma = (
                df[self.volume_col]
                .rolling(window=self.volume_ma_window, min_periods=1)
                .mean()
            )
            volume_condition = df[self.volume_col] < vol_ma
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

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "volume_col": [StrategyColumns.VOLUME],
            "short_window": [5, 10, 15, 20],
            "long_window": [30, 50, 100, 200],
            "trend_window": [100, 200, 300],
            "volume_ma_window": [10, 20, 30],
            "ma_type": [MA_Type.EMA, MA_Type.SMA],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            ),
            volume_col=trial.suggest_categorical(
                f"{prefix}volume_col", [StrategyColumns.VOLUME]
            ),
            short_window=trial.suggest_int(f"{prefix}short_window", 5, 20),
            long_window=trial.suggest_int(f"{prefix}long_window", 30, 200),
            trend_window=trial.suggest_int(f"{prefix}trend_window", 100, 300),
            volume_ma_window=trial.suggest_int(f"{prefix}volume_ma_window", 10, 30),
            ma_type=trial.suggest_categorical(
                f"{prefix}ma_type", [MA_Type.EMA, MA_Type.SMA]
            ),
        )
