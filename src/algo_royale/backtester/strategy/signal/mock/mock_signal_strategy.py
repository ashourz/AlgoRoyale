import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class MockSignalStrategy(BaseSignalStrategy):
    """
    A mock signal strategy for testing purposes.
    This strategy generates a fixed signal for testing.
    """

    def __init__(self):
        """
        Initialize the mock signal strategy with a fixed signal value.

        :param signal_value: The fixed signal value to return.
        """
        self.default_hash_id = "mock_signal_strategy"
        self.default_description = "Mock signal strategy for testing purposes."
        # Initialize with default values
        self.signal_value = self.default_signal_value
        self.required_columns = []
        self.hash_id = self.default_hash_id
        self.description = self.default_description

    def reset(self):
        """
        Reset the strategy to its initial state.
        """
        self.signal_value = None
        self.required_columns = []
        self.hash_id = self.default_hash_id
        self.description = self.default_description
        self._call_return_value = None

    def update_signal_value(
        self, signal_value: pd.DataFrame, exception_message: str = None
    ):
        """
        Update the fixed signal value.

        :param signal_value: The new fixed signal value to return.
        """
        self.signal_exception_message = exception_message
        self.signal_value = signal_value

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a fixed signal.

        :return: The fixed signal value.
        """
        if self.signal_exception_message:
            df = df.copy()
            df[SignalStrategyColumns.ENTRY_SIGNAL] = SignalType.HOLD.value
            df[SignalStrategyColumns.EXIT_SIGNAL] = SignalType.HOLD.value
            return df
        if self.signal_value is None:
            raise ValueError(
                "Signal value is not set. Please set it before generating signals."
            )
        # Return the fixed signal value
        return self.signal_value

    @property
    def required_columns(self) -> list[str]:
        """
        Return the required columns for this strategy.

        :return: A list of required columns.
        """
        return self.required_columns

    def update_required_columns(self, columns: list[str]):
        """
        Update the required columns for this strategy.

        :param columns: A list of required columns.
        """
        self.required_columns = columns

    def get_description(self) -> str:
        """
        Get a description of the strategy.

        :return: A string description of the strategy.
        """
        return self.description

    def update_description(self, description: str):
        """
        Update the description of the strategy.

        :param description: A new description for the strategy.
        """
        self.description = description

    def get_hash_id(self) -> str:
        """
        Get a unique identifier for the strategy.

        :return: A string identifier for the strategy.
        """
        return self.hash_id

    def update_hash_id(self, hash_id: str):
        """
        Update the unique identifier for the strategy.

        :param hash_id: A new unique identifier for the strategy.
        """
        self.hash_id = hash_id


def mockSignalStrategy():
    """
    Create and return an instance of MockSignalStrategy.

    :return: An instance of MockSignalStrategy.
    """
    return MockSignalStrategy()
