import pandas as pd


class StrategyCondition:
    """
    Base class for all strategy filters.
    """

    def __init__(self, *args, **kwargs):
        pass

    def apply(self, df: pd.DataFrame) -> pd.Series:
        """
        Should return a boolean Series where True means the filter passes.
        """
        raise NotImplementedError("Filter must implement apply(df)")

    def __call__(self, df):
        return self.apply(df)

    @property
    def required_columns(self):
        """Override in subclasses to add additional required columns."""
        return set()
