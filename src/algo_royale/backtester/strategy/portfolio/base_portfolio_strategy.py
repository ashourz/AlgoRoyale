from abc import abstractmethod
from typing import Any, Dict

import numpy as np
import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.portfolio_execution_keys import (
    PortfolioExecutionKeys,
)
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

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        For portfolio strategies, generate a DataFrame with at least 'portfolio_returns' for evaluation.
        Expects df to contain return columns for each asset (matching allocate's expectations).
        """
        # Try to infer returns DataFrame from df
        # If df is multi-column, treat as returns; else, raise error
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(
                "Input DataFrame must be non-empty for portfolio strategies."
            )
        returns = df.copy()
        # Defensive: drop non-numeric columns if present
        returns = returns.select_dtypes(include=[np.number])
        if returns.empty:
            raise ValueError("No numeric columns found in input DataFrame for returns.")
        weights = self.allocate(returns, returns)
        # Compute portfolio returns as weighted sum of asset returns
        portfolio_returns = (weights * returns).sum(axis=1)
        result = pd.DataFrame(index=returns.index)
        result[PortfolioExecutionKeys.PORTFOLIO_RETURNS] = portfolio_returns
        return result

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

    def _mask_and_normalize_weights(
        self, weights: pd.DataFrame, prices: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Set weights to zero for assets with invalid prices (<=0 or NaN), then re-normalize each row.
        """
        valid = (prices > 0) & (~prices.isna())
        masked_weights = weights.where(valid, 0.0)
        row_sums = masked_weights.sum(axis=1)
        for idx, s in row_sums.items():
            if np.isclose(s, 0.0):
                masked_weights.loc[idx] = 0.0
            else:
                masked_weights.loc[idx] = masked_weights.loc[idx] / s
        return masked_weights
