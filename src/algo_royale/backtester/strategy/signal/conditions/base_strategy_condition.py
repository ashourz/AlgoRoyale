import itertools

import pandas as pd
from optuna import Trial

from algo_royale.logging.loggable import Loggable


class StrategyCondition:
    """
    Base class for all strategy filters.
    """

    def __init__(self, logger: Loggable = None, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.logger = logger

    def apply(self, df: pd.DataFrame) -> pd.Series:
        # Check for missing columns
        if self.logger:
            self.logger.debug(
                f"Applying {self.__class__.__name__} with params: {self.__dict__}"
            )
        missing = [col for col in self.required_columns if col not in df.columns]
        if self.logger:
            self.logger.debug(f"Missing columns: {missing}")
        if missing:
            # Return all False (or np.nan) if required columns are missing
            return pd.Series([False] * len(df), index=df.index)
        if self.logger:
            self.logger.debug(f"Required columns present: {self.required_columns}")
        # Delegate to subclass logic
        return self._apply(df)

    def __call__(self, df: pd.DataFrame) -> pd.Series:
        return self.apply(df)

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        """Subclasses implement their logic here."""
        raise NotImplementedError("Subclasses must implement _apply(df)")

    @property
    def required_columns(self):
        """Override in subclasses to add additional required columns."""
        return set()

    @property
    def window_size(self) -> int:
        """Override in subclasses to specify the window size for buffered conditions."""
        return 1

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
    def all_possible_conditions(cls, logger: Loggable):
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
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        """Should be overridden in subclasses to suggest parameters using an Optuna trial.

        Example:
            return cls(
                threshold=trial.suggest_int(f"{prefix}threshold", 20, 30),
                window=trial.suggest_int(f"{prefix}window", 10, 14)
            )
        """
        raise NotImplementedError(
            f"{cls.__name__}.optuna_suggest() must be implemented to use Optuna."
        )

    def get_id(self):
        params = []
        for k in sorted(self.__dict__):
            if k.startswith("_") or k == "debug":
                continue
            v = getattr(self, k)
            if hasattr(v, "get_id") and callable(v.get_id):
                v_str = v.get_id()
            else:
                v_str = repr(v)
            params.append(f"{k}={v_str}")
        return f"{self.__class__.__name__}({','.join(params)})"
