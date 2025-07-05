from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict

import pandas as pd


class BacktestEvaluator(ABC):
    def __init__(self, logger: Logger):
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
    from algo_royale.logging.logger_singleton import mockLogger

    logger: Logger = mockLogger()
    return BacktestEvaluator(logger=logger)
