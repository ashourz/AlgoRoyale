import itertools


class StatefulLogic:
    """Base class for stateful logic in strategies.
    This class defines the interface for stateful logic components that can be used
    in trading strategies. Each subclass should implement the `__call__` method to
    update signals and state based on the current row of data.
    """

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(
        self, i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
    ):
        """
        Dual-signal interface for stateful logic.
        Args:
            i: Current row index (int)
            df: DataFrame
            entry_signal: Current entry signal for this row (str or int)
            exit_signal: Current exit signal for this row (str or int)
            state: Mutable state object (dict or custom)
            trend_mask: Series[bool] for trend
            filter_mask: Series[bool] for filter
        Returns:
            (entry_signal, exit_signal, state): tuple
        """
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            return entry_signal, exit_signal, state
        return self._call_impl(
            i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
        )

    def _call_impl(
        self, i, df, entry_signal, exit_signal, state, trend_mask, filter_mask
    ):
        """
        Implement in subclass. Should return (entry_signal, exit_signal, state).
        """
        raise NotImplementedError("Implement in subclass")

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
                "param1": [1, 2, 3],
                "param2": [True, False]
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
        """
        params = {}
        for k, v in self.__dict__.items():
            if hasattr(v, "get_id") and callable(v.get_id):
                params[k] = v.get_id()
            else:
                params[k] = v
        param_str = ",".join(f"{k}={repr(v)}" for k, v in sorted(params.items()))
        return f"{self.__class__.__name__}({param_str})"
