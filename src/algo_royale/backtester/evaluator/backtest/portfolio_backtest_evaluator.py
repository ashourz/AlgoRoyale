from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from algo_royale.backtester.column_names.portfolio_evaluation_keys import (
    PortfolioEvaluationKeys,
)
from algo_royale.backtester.column_names.portfolio_execution_keys import (
    PortfolioExecutionKeys,
)
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.logging.loggable import Loggable


class PortfolioBacktestEvaluator(BacktestEvaluator):
    """
    Evaluates portfolio backtest results and computes performance metrics.
    """

    def __init__(self, logger: Loggable):
        super().__init__(logger)

    def _evaluate_signals(
        self, signals_df: pd.DataFrame, trades: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Evaluate portfolio backtest results and compute key performance metrics.

        Parameters:
            signals_df (pd.DataFrame): DataFrame containing backtest results. Expected columns:
                - "portfolio_values": List or array of portfolio values over time (preferred).
                  OR
                - "portfolio_returns": List, array, or pd.Series of periodic returns (if values not available).
                - "trades" (optional): List of trades or transactions (for number of trades).

        Returns:
            metrics (dict): Dictionary with the following keys:
                - "total_return": Total return over the period (float).
                - "mean_return": Mean periodic return (float).
                - "volatility": Standard deviation of periodic returns (float).
                - "sharpe_ratio": Mean return divided by volatility (float).
                - "max_drawdown": Maximum drawdown over the period (float, negative).
                - "sortino_ratio": Mean return divided by downside deviation (float).
                - "calmar_ratio": Total return divided by abs(max_drawdown) (float).
                - "win_rate": Fraction of periods with positive return (float).
                - "profit_factor": Sum of positive returns divided by sum of negative returns (float).
                - "num_trades": Number of trades (int, if trade data provided).
        """
        try:
            self.logger.info(
                "Evaluating portfolio backtest results and computing performance metrics."
            )
            self.logger.debug(
                f"[EVAL] DataFrame shape: {signals_df.shape}, columns: {signals_df.columns.tolist()}"
            )
            self.logger.debug(
                f"[EVAL] DataFrame head:\n{signals_df.head()}\nData types:\n{signals_df.dtypes}"
            )

            # Validate the input DataFrame
            self._validate_dataframe(signals_df)

            # Use portfolio_values if available, else fallback to portfolio_returns
            if signals_df.empty:
                self.logger.error("Input DataFrame is empty. Cannot compute metrics.")
                return {
                    k: np.nan
                    for k in [
                        PortfolioEvaluationKeys.TOTAL_RETURN,
                        PortfolioEvaluationKeys.MEAN_RETURN,
                        PortfolioEvaluationKeys.VOLATILITY,
                        PortfolioEvaluationKeys.SHARPE_RATIO,
                        PortfolioEvaluationKeys.MAX_DRAWDOWN,
                        PortfolioEvaluationKeys.SORTINO_RATIO,
                        PortfolioEvaluationKeys.CALMAR_RATIO,
                        PortfolioEvaluationKeys.WIN_RATE,
                        PortfolioEvaluationKeys.PROFIT_FACTOR,
                        PortfolioEvaluationKeys.NUM_TRADES,
                    ]
                }
            if PortfolioExecutionKeys.PORTFOLIO_VALUES in signals_df:
                values = pd.Series(signals_df[PortfolioExecutionKeys.PORTFOLIO_VALUES])
                self.logger.debug(
                    f"[EVAL] portfolio_values length: {len(values)}, index: {values.index}"
                )
                returns = values.pct_change().fillna(0)
            else:
                returns = pd.Series(
                    signals_df[PortfolioExecutionKeys.PORTFOLIO_RETURNS]
                )
                self.logger.debug(
                    f"[EVAL] portfolio_returns length: {len(returns)}, index: {returns.index}"
                )
            # Defensive: drop NaN/inf
            returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
            self.logger.debug(
                f"[EVAL] Cleaned returns length: {len(returns)}, head: {returns.head()}"
            )
            if returns.empty or (returns == 0).all():
                self.logger.error(
                    "No valid or non-zero returns in input DataFrame. Cannot compute metrics."
                )
                return {
                    k: np.nan
                    for k in [
                        PortfolioEvaluationKeys.TOTAL_RETURN,
                        PortfolioEvaluationKeys.MEAN_RETURN,
                        PortfolioEvaluationKeys.VOLATILITY,
                        PortfolioEvaluationKeys.SHARPE_RATIO,
                        PortfolioEvaluationKeys.MAX_DRAWDOWN,
                        PortfolioEvaluationKeys.SORTINO_RATIO,
                        PortfolioEvaluationKeys.CALMAR_RATIO,
                        PortfolioEvaluationKeys.WIN_RATE,
                        PortfolioEvaluationKeys.PROFIT_FACTOR,
                        PortfolioEvaluationKeys.NUM_TRADES,
                    ]
                }
            # Metrics
            total_return = float((returns + 1).prod() - 1)
            mean_return = float(returns.mean())
            volatility = float(returns.std())
            sharpe_ratio = float(returns.mean() / (returns.std() + 1e-8))
            max_dd = float(self.max_drawdown(returns))
            sortino_ratio = float(self.sortino_ratio(returns))
            calmar_ratio = float(total_return / abs(max_dd)) if max_dd != 0 else np.nan
            win_rate = float((returns > 0).sum() / len(returns))
            profit_factor = self.profit_factor(returns)
            num_trades = None
            if trades is not None:
                num_trades = len(trades)
            self.logger.debug(
                f"[EVAL] Metrics: total_return={total_return}, mean_return={mean_return}, volatility={volatility}, sharpe_ratio={sharpe_ratio}, max_drawdown={max_dd}, sortino_ratio={sortino_ratio}, calmar_ratio={calmar_ratio}, win_rate={win_rate}, profit_factor={profit_factor}, num_trades={num_trades}"
            )
            metrics = {
                PortfolioEvaluationKeys.TOTAL_RETURN: total_return,
                PortfolioEvaluationKeys.MEAN_RETURN: mean_return,
                PortfolioEvaluationKeys.VOLATILITY: volatility,
                PortfolioEvaluationKeys.SHARPE_RATIO: sharpe_ratio,
                PortfolioEvaluationKeys.MAX_DRAWDOWN: max_dd,
                PortfolioEvaluationKeys.SORTINO_RATIO: sortino_ratio,
                PortfolioEvaluationKeys.CALMAR_RATIO: calmar_ratio,
                PortfolioEvaluationKeys.WIN_RATE: win_rate,
                PortfolioEvaluationKeys.PROFIT_FACTOR: profit_factor,
            }
            if num_trades is not None:
                metrics[PortfolioEvaluationKeys.NUM_TRADES] = num_trades
            return metrics
        except Exception as e:
            self.logger.error(f"[EVAL] Evaluation failed: {e}")
            self.logger.debug("[EVAL] Exception details:", exc_info=True)
            raise ValueError(
                f"Evaluation failed: {e}. Please check the input DataFrame and ensure it contains valid data."
            )

    def evaluate_from_dict(self, result: dict) -> dict:
        """
        Evaluate portfolio backtest results from a result dictionary.
        """
        # Build DataFrame for evaluation
        if (
            PortfolioExecutionKeys.PORTFOLIO_VALUES in result
            and PortfolioExecutionKeys.PORTFOLIO_RETURNS in result
        ):
            df = pd.DataFrame(
                {
                    PortfolioExecutionKeys.PORTFOLIO_VALUES: result[
                        PortfolioExecutionKeys.PORTFOLIO_VALUES
                    ],
                    PortfolioExecutionKeys.PORTFOLIO_RETURNS: result[
                        PortfolioExecutionKeys.PORTFOLIO_RETURNS
                    ],
                }
            )
        elif PortfolioExecutionKeys.PORTFOLIO_VALUES in result:
            df = pd.DataFrame(
                {
                    PortfolioExecutionKeys.PORTFOLIO_VALUES: result[
                        PortfolioExecutionKeys.PORTFOLIO_VALUES
                    ]
                }
            )
            df[PortfolioExecutionKeys.PORTFOLIO_RETURNS] = (
                pd.Series(result[PortfolioExecutionKeys.PORTFOLIO_VALUES])
                .pct_change()
                .fillna(0)
            )
        elif PortfolioExecutionKeys.PORTFOLIO_RETURNS in result:
            df = pd.DataFrame(
                {
                    PortfolioExecutionKeys.PORTFOLIO_RETURNS: result[
                        PortfolioExecutionKeys.PORTFOLIO_RETURNS
                    ]
                }
            )
        else:
            self.logger.error(
                "No portfolio_values or portfolio_returns in result dict."
            )
            return {}
        # Optionally add trades if present
        trades = (
            result[PortfolioExecutionKeys.TRANSACTIONS]
            if PortfolioExecutionKeys.TRANSACTIONS in result
            else None
        )
        return self._evaluate_signals(df, trades=trades)

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Validate the DataFrame for required columns, null values, and invalid data.
        At least one of 'portfolio_values' or 'portfolio_returns' must be present.
        Only check for nulls in columns that exist.
        Parameters:
            df: The DataFrame to validate.
        """
        if not (
            PortfolioExecutionKeys.PORTFOLIO_VALUES in df.columns
            or PortfolioExecutionKeys.PORTFOLIO_RETURNS in df.columns
        ):
            self.logger.error(
                "Missing both 'portfolio_values' and 'portfolio_returns' columns."
            )
            raise ValueError(
                "At least one of 'portfolio_values' or 'portfolio_returns' must be present in the DataFrame."
            )
        for col in [
            PortfolioExecutionKeys.PORTFOLIO_VALUES,
            PortfolioExecutionKeys.PORTFOLIO_RETURNS,
        ]:
            if col in df.columns and df[col].isnull().any():
                self.logger.error(f"Null values found in column: {col}")
                raise ValueError(f"Null values found in column: {col}")

    @staticmethod
    def max_drawdown(returns: pd.Series) -> float:
        cum_returns = (1 + returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return drawdown.min()

    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        downside = returns[returns < risk_free_rate]
        downside_std = downside.std() if len(downside) > 0 else 0.0
        if downside_std == 0:
            return np.nan
        return (returns.mean() - risk_free_rate) / (downside_std + 1e-8)

    @staticmethod
    def profit_factor(returns: pd.Series) -> float:
        gains = returns[returns > 0].sum()
        losses = -returns[returns < 0].sum()
        if losses == 0:
            return np.inf
        return float(gains / losses)


def mockPortfolioBacktestEvaluator() -> PortfolioBacktestEvaluator:
    """Creates a mock PortfolioBacktestEvaluator for testing purposes."""
    from algo_royale.logging.logger_factory import mockLogger

    logger: Loggable = mockLogger()
    return PortfolioBacktestEvaluator(logger=logger)
