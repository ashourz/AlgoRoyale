import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def price_crosses_below_sma(
    current_row,
    prev_row,
    close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    sma_col: StrategyColumns = StrategyColumns.SMA_20,
):
    """
    Returns True if the price crosses below the SMA between the previous and current rows.
    This indicates a potential shift into a downtrend.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        sma_col (str): Column name for the SMA values.
        close_col (str): Column name for the close price.

    Returns:
        bool: True if price crosses below SMA, else False.
    """
    return (
        prev_row[close_col] >= prev_row[sma_col]
        and current_row[close_col] < current_row[sma_col]
    )


class PriceCrossesBelowSMACondition(StrategyCondition):
    """Condition to check if the price crosses below a Simple Moving Average (SMA).
    This condition checks if the current price crosses below the SMA,
    indicating a potential bearish trend. It is typically used in trend-following strategies
    to identify potential sell signals when the price is below the SMA.
    This condition is applied to each row of a DataFrame containing price and SMA values.
    This condition is useful for strategies that require the price to cross below a certain SMA
    to enter trades.

    Args:
        close_col (StrategyColumns): Column name for the close price.
        sma_col (StrategyColumns): Column name for the SMA values.

    Returns:
        pd.Series: Boolean Series where True indicates the price crosses below the SMA.

    Usage:
        filter = PriceCrossesBelowSMAFilter(close_col='Close', sma_col='SMA_50')
        df['price_crosses_below_sma'] = filter.apply(df)
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
    ):
        super().__init__(close_col=close_col, sma_col=sma_col)
        self.close_col = close_col
        self.sma_col = sma_col

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: price_crosses_below_sma(
                row, df.shift(1).loc[row.name], self.sma_col, self.close_col
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.close_col, self.sma_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "sma_col": [
                StrategyColumns.SMA_10,
                StrategyColumns.SMA_20,
                StrategyColumns.SMA_50,
                StrategyColumns.SMA_100,
                StrategyColumns.SMA_150,
                StrategyColumns.SMA_200,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            ),
            sma_col=trial.suggest_categorical(
                f"{prefix}sma_col",
                [
                    StrategyColumns.SMA_10,
                    StrategyColumns.SMA_20,
                    StrategyColumns.SMA_50,
                    StrategyColumns.SMA_100,
                    StrategyColumns.SMA_150,
                    StrategyColumns.SMA_200,
                ],
            ),
        )
