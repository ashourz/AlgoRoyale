from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

from algo_royale.logging.loggable import Loggable


class BacktestEvaluator(ABC):
    def __init__(self, logger: Loggable):
        self.logger = logger

    def evaluate(self, strategy, df: pd.DataFrame) -> Dict[str, float]:
        try:
            if not isinstance(df, pd.DataFrame):
                self.logger.error(
                    f"Invalid DataFrame provided for evaluation: {df}. Must be a pandas DataFrame."
                )
                return {}
            if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                self.logger.error(
                    "DataFrame is None, not a DataFrame, or empty. Cannot evaluate strategy."
                )
                return {}
            if not df.empty and isinstance(df, pd.DataFrame):
                signals_df = strategy.generate_signals(df.copy())
                return self._evaluate_signals(signals_df)
            else:
                self.logger.error(
                    f"Invalid DataFrame provided for evaluation: {df}. Must be a non-empty pandas DataFrame."
                )
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise

    def evaluate_from_dict(self, result: dict) -> dict:
        """
        Evaluate from a backtest result dictionary (default: not implemented).
        Subclasses should override if they support dict input.
        """
        raise NotImplementedError(
            "evaluate_from_dict is not implemented for this evaluator."
        )

    @abstractmethod
    def _evaluate_signals(self, signals_df: pd.DataFrame) -> dict:
        pass


def mockBacktestEvaluator() -> BacktestEvaluator:
    """Creates a mock BacktestEvaluator for testing purposes."""
    from algo_royale.logging.logger_factory import mockLogger

    logger: Loggable = mockLogger()
    return BacktestEvaluator(logger=logger)
