from abc import ABC, abstractmethod

import pandas as pd


class TrendFunction(ABC):
    @property
    def required_columns(self):
        """Override in subclasses to add additional required columns."""
        return set()

    @abstractmethod
    def __call__(self, df: pd.DataFrame) -> pd.Series:
        pass
