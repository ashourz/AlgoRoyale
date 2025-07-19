import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def price_crosses_above_sma(
    current_row,
    prev_row,
    sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
    close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
    debug: bool = False,
):
    """
    Returns True if the price crosses above the SMA between the previous and current rows.
    This indicates a potential shift into an uptrend.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        sma_col (str): Column name for the SMA values.
        close_col (str): Column name for the close price.

    Returns:
        bool: True if price crosses above SMA, else False.
    """
    crossed = (
        prev_row[close_col] <= prev_row[sma_col]
        and current_row[close_col] > current_row[sma_col]
    )
    if crossed:
        if debug:
            print(
                f"Cross above detected at index {current_row.name}: "
                f"prev_close={prev_row[close_col]}, prev_sma={prev_row[sma_col]}, "
                f"curr_close={current_row[close_col]}, curr_sma={current_row[sma_col]}"
            )
    return crossed


class PriceAboveSMACondition(StrategyCondition):
    """Condition to check if the price is above a Simple Moving Average (SMA).
    This condition checks if the current price crosses above the SMA,
    indicating a potential bullish trend. It is typically used in trend-following strategies
    to identify potential buy signals when the price is above the SMA.
    This condition is applied to each row of a DataFrame containing price and SMA values.
    This condition is useful for strategies that require the price to be above a certain SMA
    to enter trades.

    Args:
        close_col (StrategyColumns): Column name for the close price.
        sma_col (StrategyColumns): Column name for the SMA values.
    Returns:
        pd.Series: Boolean Series where True indicates the price is above the SMA.
    Usage:
        filter = PriceAboveSMAFilter(close_col='Close', sma_col='SMA_50')
        df['price_above_sma'] = filter.apply(df)
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
    ):
        super().__init__(close_col=close_col, sma_col=sma_col)
        self.close_col = close_col
        self.sma_col = sma_col
        # TODO: pull from config
        self.debug = False

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: price_crosses_above_sma(
                row, df.shift(1).loc[row.name], self.sma_col, self.close_col, self.debug
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.close_col, self.sma_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "sma_col": [
                SignalStrategyColumns.SMA_10,
                SignalStrategyColumns.SMA_20,
                SignalStrategyColumns.SMA_50,
                SignalStrategyColumns.SMA_100,
                SignalStrategyColumns.SMA_150,
                SignalStrategyColumns.SMA_200,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
            sma_col=trial.suggest_categorical(
                f"{prefix}sma_col",
                [
                    SignalStrategyColumns.SMA_10,
                    SignalStrategyColumns.SMA_20,
                    SignalStrategyColumns.SMA_50,
                    SignalStrategyColumns.SMA_100,
                    SignalStrategyColumns.SMA_150,
                    SignalStrategyColumns.SMA_200,
                ],
            ),
        )
