from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

from algo_royale.logging.loggable import Loggable


class BacktestEvaluator(ABC):
    def __init__(self, logger: Loggable):
        self.logger = logger

    def evaluate(self, strategy, df: pd.DataFrame) -> Dict[str, float]:
        try:
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

    @abstractmethod
    def _evaluate_signals(self, signals_df: pd.DataFrame) -> dict:
        pass


def mockBacktestEvaluator() -> BacktestEvaluator:
    """Creates a mock BacktestEvaluator for testing purposes."""
    from algo_royale.logging.logger_factory import mockLogger

    logger: Loggable = mockLogger()
    return BacktestEvaluator(logger=logger)
