import itertools
from logging import Logger

import pandas as pd
from optuna import Trial


class StrategyCondition:
    """
    Base class for all strategy filters.
    """

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

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
    def available_param_grid(cls) -> dict:
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
    def all_possible_conditions(cls, logger: Logger):
        """
        Returns all possible instances of this condition class with different parameter combinations.
        If no parameters are defined, returns a single instance of the class.
        """
        grid = cls.available_param_grid()
        logger.debug(f"Available param grid for {cls.__name__}: {grid}")
        if not grid:
            return [cls()]
        keys = list(grid.keys())
        values = list(grid.values())
        logger.debug(f"Keys: {keys}, Values: {values}")
        combos = []
        for prod in itertools.product(*values):
            params = dict(zip(keys, prod))
            combos.append(cls(**params))
        return combos

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            period=trial.suggest_int(f"{prefix}period", 10, 30),
            threshold=trial.suggest_float(f"{prefix}threshold", 0.2, 0.8),
        )

    def get_id(self):
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
