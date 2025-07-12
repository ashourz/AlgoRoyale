from abc import ABC, abstractmethod
from typing import Dict
from algo_royale.logging.loggable import Loggable

import pandas as pd


class BacktestEvaluator(ABC):
    def __init__(self, logger: Loggable):
        self.logger = logger

    def evaluate(self, strategy, df: pd.DataFrame) -> Dict[str, float]:
        try:
            signals_df = strategy.generate_signals(df.copy())
            return self._evaluate_signals(signals_df)
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
