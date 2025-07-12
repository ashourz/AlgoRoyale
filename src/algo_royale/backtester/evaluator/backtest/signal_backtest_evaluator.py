from logging import Logger

import numpy as np
import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enum.signal_type import SignalType
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)


class SignalBacktestEvaluator(BacktestEvaluator):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def _evaluate_signals(self, signals_df: pd.DataFrame) -> dict:
        try:
            self.logger.debug(
                f"Evaluating signals DataFrame with {len(signals_df)} rows"
            )

            # Validate the input DataFrame
            self._validate_dataframe(signals_df)

            trades = self._simulate_trades(signals_df)
            self.logger.debug(f"Trades simulated: {len(trades)}")
            if not trades:
                return {
                    "total_return": 0.0,
                    "sharpe_ratio": 0.0,
                    "win_rate": 0.0,
                    "max_drawdown": 0.0,
                }

            returns = np.array([t["return"] for t in trades])
            win_rate = (
                np.sum(returns > 0) / np.sum(returns != 0)
                if np.any(returns != 0)
                else 0.0
            )
            sharpe = self._sharpe_ratio(returns)
            drawdown = self._max_drawdown([t["cumulative_return"] for t in trades])

            return {
                "total_return": float(np.sum(returns)),
                "sharpe_ratio": float(sharpe),
                "win_rate": float(win_rate),
                "max_drawdown": float(drawdown),
            }

        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise ValueError(
                f"Evaluation failed: {e}. Please check the input DataFrame and ensure it contains valid data."
            )

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Validate the DataFrame for required columns, null values, invalid data, and extreme values.
        Parameters:
            df: The DataFrame to validate.
        """
        essential_cols = [
            SignalStrategyColumns.TIMESTAMP,
            SignalStrategyColumns.CLOSE_PRICE,
            SignalStrategyColumns.ENTRY_SIGNAL,
            SignalStrategyColumns.EXIT_SIGNAL,
        ]
        for col in essential_cols:
            if col not in df.columns:
                self.logger.error(f"Missing essential column: {col}")
                raise ValueError(f"Missing essential column: {col}")
            if df[col].isnull().any():
                self.logger.error(f"Null values found in column: {col}")
                raise ValueError(f"Null values found in column: {col}")

        if (df[SignalStrategyColumns.CLOSE_PRICE] <= 0).any():
            self.logger.error("Invalid close prices (<= 0) detected")
            raise ValueError("Invalid close prices (<= 0) detected")

        if (df[SignalStrategyColumns.CLOSE_PRICE] > 1e6).any():
            self.logger.warning(
                "Extreme close prices (> 1e6) detected. These will be skipped."
            )

    def _simulate_trades(self, df: pd.DataFrame) -> list[dict]:
        """
        Simulate trades based on entry and exit signals in the DataFrame.
        Includes validation for numerical stability and extreme values.
        """
        try:
            entry_col = SignalStrategyColumns.ENTRY_SIGNAL
            exit_col = SignalStrategyColumns.EXIT_SIGNAL
            close_col = SignalStrategyColumns.CLOSE_PRICE

            trades = []
            in_trade = False
            entry_price = None
            cumulative_return = 0.0

            for i, row in df.iterrows():
                signal_entry = row[entry_col]
                signal_exit = row[exit_col]
                price = row[close_col]

                if not np.isfinite(price) or price <= 0 or price > 1e6:
                    self.logger.warning(
                        f"Skipping trade simulation at index {i} due to invalid price: {price}"
                    )
                    continue

                if signal_entry == SignalType.BUY.value and not in_trade:
                    entry_price = price
                    in_trade = True

                elif signal_exit == SignalType.SELL.value and in_trade:
                    if entry_price is None or not np.isfinite(entry_price):
                        self.logger.warning(
                            f"Skipping trade simulation at index {i} due to invalid entry price: {entry_price}"
                        )
                        continue

                    pnl = (price - entry_price) / entry_price
                    if not np.isfinite(pnl):
                        self.logger.warning(
                            f"Skipping trade simulation at index {i} due to invalid PnL calculation: {pnl}"
                        )
                        continue

                    cumulative_return += pnl
                    trades.append(
                        {
                            "index": i,
                            "entry_price": entry_price,
                            "exit_price": price,
                            "return": pnl,
                            "cumulative_return": cumulative_return,
                            "timestamp": row[SignalStrategyColumns.TIMESTAMP],
                        }
                    )
                    in_trade = False
                    entry_price = None

            return trades
        except Exception as e:
            self.logger.error(f"Trade simulation failed: {e}")
            raise ValueError(f"Trade simulation failed: {e}")

    def _sharpe_ratio(self, returns: np.ndarray, risk_free_rate=0.0) -> float:
        try:
            if len(returns) < 2:
                return 0.0
            excess_returns = returns - risk_free_rate
            std = np.std(excess_returns, ddof=1)
            if std == 0:
                return 0.0
            return np.mean(excess_returns) / std
        except Exception as e:
            self.logger.error(f"Sharpe ratio calculation failed: {e}")
            return 0.0

    def _max_drawdown(self, cumulative_returns: list[float]) -> float:
        try:
            if not cumulative_returns:
                return 0.0
            cum_returns = np.array(cumulative_returns)
            peak = np.maximum.accumulate(cum_returns)
            drawdown = peak - cum_returns
            return np.max(drawdown)
        except Exception as e:
            self.logger.error(f"Max drawdown calculation failed: {e}")
            return 0.0


def mockSignalBacktestEvaluator() -> SignalBacktestEvaluator:
    """Creates a mock SignalBacktestEvaluator for testing purposes."""
    from algo_royale.logging.logger_factory import mockLogger

    logger: Logger = mockLogger()
    return SignalBacktestEvaluator(logger=logger)
