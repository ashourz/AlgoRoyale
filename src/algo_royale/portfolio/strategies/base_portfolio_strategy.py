from abc import abstractmethod
from typing import Any, Dict

import pandas as pd
from optuna import Trial

from algo_royale.backtester.strategy.base_strategy import BaseStrategy


class BasePortfolioStrategy(BaseStrategy):
    """
    Abstract base class for portfolio allocation strategies.
    """

    def __init__(self, optimization_options: Dict[str, Any] = None):
        self.optimization_options = optimization_options or {}

    @property
    def required_columns(self):
        """Override in subclasses to specify required columns for the strategy."""
        return set()

    def get_description(self) -> str:
        params = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({params})"

    def get_id(self) -> str:
        params = []
        for k in sorted(self.__dict__):
            if k.startswith("_"):
                continue
            v = getattr(self, k)
            if hasattr(v, "get_id") and callable(v.get_id):
                v_str = v.get_id()
            else:
                v_str = repr(v)
            params.append(f"{k}={v_str}")
        return f"{self.__class__.__name__}({','.join(params)})"

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        """
        Should be overridden in subclasses to suggest parameters using an Optuna trial.
        """
        raise NotImplementedError(
            f"{cls.__name__}.optuna_suggest() must be implemented to use Optuna."
        )

    @abstractmethod
    def allocate(self, signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Given signals and/or returns, produce a DataFrame of portfolio weights over time.
        Args:
            signals: DataFrame of signals (index: datetime, columns: symbols)
            returns: DataFrame of returns (index: datetime, columns: symbols)
        Returns:
            DataFrame of weights (index: datetime, columns: symbols)
        """
        pass
