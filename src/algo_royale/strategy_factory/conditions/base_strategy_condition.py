import itertools

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

    @classmethod
    def available_param_grid(cls):
        """
        Should be overridden in subclasses to return a dict of parameter names to lists of possible values.
        Example:
            return {
                "threshold": [20, 25, 30],
                "window": [10, 14]
            }
        """
        return {}

    @classmethod
    def all_possible_conditions(cls):
        """
        Returns a list of all possible condition instances for this class,
        using the available_param_grid.
        """
        grid = cls.available_param_grid()
        if not grid:
            return [cls()]
        keys, values = zip(*grid.items())
        combos = [dict(zip(keys, v)) for v in itertools.product(*values)]
        return [cls(**params) for params in combos]

    def get_id(self):
        """
                Returns a unique string identifier for this logic instance,
                including the class name and its parameters.
        ]"""
        params = {}
        for k, v in self.__dict__.items():
            if hasattr(v, "get_id") and callable(v.get_id):
                params[k] = v.get_id()
            else:
                params[k] = v
        param_str = ",".join(f"{k}={repr(v)}" for k, v in sorted(params.items()))
        return f"{self.__class__.__name__}({param_str})"
