from abc import ABC, abstractmethod
from typing import Any, Dict

import pandas as pd


class BacktestExecutor(ABC):
    """Base class for backtest executors.
    This class provides the interface for running backtests on portfolio strategies.
    It defines the method `run_backtest` which should be implemented by subclasses.
    """

    def __init__(self):
        """Initialize the base backtest executor."""
        pass

    @abstractmethod
    def run_backtest(
        self,
        strategy,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run a backtest for the given strategy and data.
        Parameters:
            : strategy: Strategy instance implementing allocation logic.
            : data: DataFrame containing asset prices or returns/signals.
        Returns:
            : Dictionary containing portfolio values, cash history, holdings history, and transactions.
        """
        raise NotImplementedError("Subclasses must implement run_backtest method.")

    @abstractmethod
    async def run_backtest_async(
        self,
        strategy,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run a backtest for the given strategy and data.
        Parameters:
            : strategy: Strategy instance implementing allocation logic.
            : data: DataFrame containing asset prices or returns/signals.
        Returns:
            : Dictionary containing portfolio values, cash history, holdings history, and transactions.
        """
        raise NotImplementedError("Subclasses must implement run_backtest method.")
