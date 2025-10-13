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

    def get_description(self) -> str:
        """Return a human-readable description for the wrapped strategy.

        The underlying BasePortfolioStrategy implementations expose get_description().
        Delegate to that so callers (including OrderGenerator and registry diagnostics)
        can call get_description() on the buffered wrapper transparently.
        """
        try:
            return self.strategy.get_description()
        except Exception:
            # Fall back to class name if underlying strategy doesn't provide description
            return self.get_strategy_name()

    def update(
        self, roster: dict[str, SignalDataPayload]
    ) -> dict[str, pd.DataFrame] | None:
        """
        Update the buffered portfolio strategy with the latest roster of signals.

        Returns:
            dict: A dictionary with:
                - "weights": DataFrame of portfolio weights (index: timestamp, columns: symbols, values: weights for each symbol at each timestamp).
                - "data": DataFrame of the latest roster snapshot (one row per symbol, columns for signals and price data).

        Example:
            {
                "weights": pd.DataFrame({
                    "AAPL": [0.4],
                    "MSFT": [0.3],
                    "GOOG": [0.3]
                }, index=[pd.Timestamp("2025-08-09T10:00:00")]),

                "data": pd.DataFrame([
                    {
                        "SYMBOL": "AAPL",
                        "ENTRY_SIGNAL": 1.0,
                        "EXIT_SIGNAL": 0.0,
                        "TIMESTAMP": "2025-08-09T10:00:00",
                        "OPEN_PRICE": 190.0,
                        "HIGH_PRICE": 192.0,
                        "LOW_PRICE": 189.0,
                        "CLOSE_PRICE": 190.5
                    },
                    {
                        "SYMBOL": "MSFT",
                        "ENTRY_SIGNAL": 0.5,
                        "EXIT_SIGNAL": 0.0,
                        "TIMESTAMP": "2025-08-09T10:00:00",
                        "OPEN_PRICE": 320.0,
                        "HIGH_PRICE": 322.0,
                        "LOW_PRICE": 319.0,
                        "CLOSE_PRICE": 320.1
                    },
                    {
                        "SYMBOL": "GOOG",
                        "ENTRY_SIGNAL": 0.8,
                        "EXIT_SIGNAL": 0.0,
                        "TIMESTAMP": "2025-08-09T10:00:00",
                        "OPEN_PRICE": 2700.0,
                        "HIGH_PRICE": 2710.0,
                        "LOW_PRICE": 2695.0,
                        "CLOSE_PRICE": 2700.0
                    }
                ])
            }
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
