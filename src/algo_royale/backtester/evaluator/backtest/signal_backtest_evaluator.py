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
            raise

    def _simulate_trades(self, df: pd.DataFrame) -> list[dict]:
        """Simulate trades based on entry and exit signals in the DataFrame."""
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

            if signal_entry == SignalType.BUY.value and not in_trade:
                entry_price = price
                in_trade = True

            elif signal_exit == SignalType.SELL.value and in_trade:
                pnl = (price - entry_price) / entry_price
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

    def _sharpe_ratio(self, returns: np.ndarray, risk_free_rate=0.0) -> float:
        if len(returns) < 2:
            return 0.0
        excess_returns = returns - risk_free_rate
        std = np.std(excess_returns, ddof=1)
        if std == 0:
            return 0.0
        return np.mean(excess_returns) / std

    def _max_drawdown(self, cumulative_returns: list[float]) -> float:
        if not cumulative_returns:
            return 0.0
        cum_returns = np.array(cumulative_returns)
        peak = np.maximum.accumulate(cum_returns)
        drawdown = peak - cum_returns
        return np.max(drawdown)


def mockSignalBacktestEvaluator() -> SignalBacktestEvaluator:
    """Creates a mock SignalBacktestEvaluator for testing purposes."""
    from algo_royale.logging.logger_singleton import mockLogger

    logger: Logger = mockLogger()
    return SignalBacktestEvaluator(logger=logger)
