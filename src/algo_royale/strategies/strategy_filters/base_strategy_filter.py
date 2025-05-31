import pandas as pd


class StrategyFilter:
    """
    Base class for all strategy filters.
    """

    def __init__(self, *args, **kwargs):
        pass

    def apply(self, df: pd.DataFrame) -> pd.Series:  # noqa: F821
        """
        Should return a boolean Series where True means the filter passes.
        """
        raise NotImplementedError("Filter must implement apply(df)")
