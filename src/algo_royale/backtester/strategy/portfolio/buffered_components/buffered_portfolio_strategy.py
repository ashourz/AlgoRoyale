from collections import deque

import pandas as pd

from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.strategy.base_strategy import BaseStrategy
from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


class BufferedPortfolioStrategy(BaseStrategy):
    def __init__(
        self,
        strategy: BasePortfolioStrategy,
        asset_matrix_preparer: AssetMatrixPreparer,
        logger: Loggable = None,
    ):
        self.logger = logger
        self.strategy = strategy
        self.asset_matrix_preparer = asset_matrix_preparer
        self.window_size = (
            strategy.window_size if strategy.window_size is not None else 1
        )
        self.buffer = deque(maxlen=self.window_size)

    def get_strategy_name(self) -> str:
        return self.strategy.__class__.__name__

    def update(
        self, roster: dict[str, SignalDataPayload]
    ) -> dict[str, pd.DataFrame] | None:
        """
        Update the buffered portfolio strategy with the latest roster of signals.
        """
        try:
            self.buffer.append(roster)
            if not self.buffer:
                return None
            if len(self.buffer) < self.window_size:
                return None  # Not enough data yet
            if len(self.buffer) > self.window_size:
                self.buffer.pop()
            combined_df = self._roster_buffer_to_df()
            matrix = self._roster_buffer_to_matrix(combined_df)
            weights = self.strategy.allocate(matrix)
            return {"weights": weights, "roster": roster}
        except Exception as e:
            self.logger.error(f"Error updating buffered portfolio strategy: {e}")
            return None

    def _roster_buffer_to_df(self) -> pd.DataFrame:
        """
        Convert the roster buffer to a DataFrame.
        """
        rows = []
        for symbol, payload in self.buffer.items():
            try:
                row = {
                    SignalStrategyColumns.SYMBOL: symbol,
                    SignalStrategyColumns.ENTRY_SIGNAL: payload.signals.get(
                        SignalStrategyColumns.ENTRY_SIGNAL
                    ),
                    SignalStrategyColumns.EXIT_SIGNAL: payload.signals.get(
                        SignalStrategyColumns.EXIT_SIGNAL
                    ),
                    SignalStrategyColumns.TIMESTAMP: payload.price_data.get(
                        SignalStrategyColumns.TIMESTAMP
                    ),
                    SignalStrategyColumns.OPEN_PRICE: payload.price_data.get(
                        SignalStrategyColumns.OPEN_PRICE
                    ),
                    SignalStrategyColumns.HIGH_PRICE: payload.price_data.get(
                        SignalStrategyColumns.HIGH_PRICE
                    ),
                    SignalStrategyColumns.LOW_PRICE: payload.price_data.get(
                        SignalStrategyColumns.LOW_PRICE
                    ),
                    SignalStrategyColumns.CLOSE_PRICE: payload.price_data.get(
                        SignalStrategyColumns.CLOSE_PRICE
                    ),
                }
                rows.append(row)
            except Exception as e:
                self.logger.error(
                    f"Error processing symbol {symbol} | payload {payload}: {e}"
                )
        return pd.DataFrame(rows)

    def _roster_buffer_to_matrix(self, combined_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the roster buffer to a matrix suitable for allocation.
        """
        matrix = self.asset_matrix_preparer.prepare(
            df=combined_df,
            symbol_col=SignalStrategyColumns.SYMBOL,
            timestamp_col=SignalStrategyColumns.TIMESTAMP,
        )
        ## Fill forward
        matrix = matrix.ffill()
        return matrix
