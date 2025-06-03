class StatefulLogic:
    """Base class for stateful logic in strategies.
    This class defines the interface for stateful logic components that can be used
    in trading strategies. Each subclass should implement the `__call__` method to
    update signals and state based on the current row of data.
    """

    def __call__(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
        """
        Update signals and state for the i-th row.
        Should return (signal, state).
        """
        raise NotImplementedError("Implement in subclass")

    @property
    def required_columns(self):
        """Override in subclasses to add additional required columns."""
        return set()

    def condition_id(self):
        """
        Returns a unique string identifier for this condition instance,
        including the class name and its parameters.
        If a parameter is itself a StatefulLogic, include its condition_id.
        """
        params = {}
        for k, v in self.__dict__.items():
            if isinstance(v, StatefulLogic):
                params[k] = v.condition_id()
            else:
                params[k] = v
        param_str = ",".join(f"{k}={repr(v)}" for k, v in sorted(params.items()))
        return f"{self.__class__.__name__}({param_str})"
