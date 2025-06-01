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
