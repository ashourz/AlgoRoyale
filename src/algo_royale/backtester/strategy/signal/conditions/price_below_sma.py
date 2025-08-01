import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


@staticmethod
def price_below_sma(
    row,
    sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
    close_col=SignalStrategyColumns.CLOSE_PRICE,
):
    """
    Returns True if the price is below the SMA (indicating downtrend),
    else False.

    Args:
        row (pd.Series): A row of data.
        sma_col (str): Column name for SMA.
        close_col (str): Column name for close price.

    Returns:
        bool: True if price < SMA, else False.
    """
    return row[close_col] < row[sma_col]


class PriceBelowSMACondition(StrategyCondition):
    """Condition to check if the price is below a Simple Moving Average (SMA).
    This condition checks if the current price is below the SMA,
    indicating a potential bearish trend. It is typically used in trend-following strategies
    to identify potential sell signals when the price is below the SMA.
    This condition is applied to each row of a DataFrame containing price and SMA values.
    This condition is useful for strategies that require the price to be below a certain SMA
    to enter trades.

    Args:
        close_col (str): Column name for the close price.
        sma_col (str): Column name for the SMA values.

    Returns:
        pd.Series: Boolean Series where True indicates the price is below the SMA.

    Usage:
        filter = PriceBelowSMAFilter(close_col='Close', sma_col='SMA_50')
        df['price_below_sma'] = filter.apply(df)
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        logger: Loggable = None,
    ):
        super().__init__(close_col=close_col, sma_col=sma_col, logger=logger)
        self.close_col = close_col
        self.sma_col = sma_col

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: price_below_sma(row, self.sma_col, self.close_col),
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
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
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
