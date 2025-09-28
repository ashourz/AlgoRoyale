import pandas as pd

from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.logging.loggable import Loggable


class MockPortfolioStrategy(BaseSignalStrategy):
    """
    A mock portfolio strategy for testing purposes.
    This strategy generates a fixed signal for testing.
    """

    def __init__(self):
        """
        Initialize the mock portfolio strategy with a fixed signal value.
        """
        self.default_hash_id = "mock_portfolio_strategy"
        self.default_description = "Mock portfolio strategy for testing purposes."
        # Initialize with default values
        self.signal_value = getattr(self, "default_signal_value", None)
        self._required_columns = []
        self.hash_id = self.default_hash_id
        self.description = self.default_description
        # By default, always return a valid weights DataFrame for any symbol
        self._allocate_return_value = pd.DataFrame({"AAPL": [1.0]})
        self._optuna_suggest_return_value = None

    def reset(self):
        """
        Reset the strategy to its initial state.
        """
        self.signal_value = None
        self.required_columns = []
        self.id = self.default_hash_id
        self.description = self.default_description
        self._call_return_value = None
        self._allocate_return_value = None

    def update_signal_value(self, signal_value: pd.DataFrame):
        """
        Update the fixed signal value.

        :param signal_value: The new fixed signal value to return.
        """
        self.signal_value = signal_value

    def generate_signals(self, logger: Loggable, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate a fixed signal.

        :return: The fixed signal value.
        """
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
        """
        return self._required_columns

    @required_columns.setter
    def required_columns(self, value):
        self._required_columns = value

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

    def get_id(self) -> str:
        """
        Get a unique identifier for the strategy.

        :return: A string identifier for the strategy.
        """
        return self.id

    def update_id(self, id: str):
        """
        Update the unique identifier for the strategy.

        :param hash_id: A new unique identifier for the strategy.
        """
        self.id = id

    @classmethod
    def update_optuna_suggest_return_value(cls, value):
        """
        Update the return value for the optuna_suggest method.

        :param value: The new return value for optuna_suggest.
        """
        cls._optuna_suggest_return_value = value

    @classmethod
    def optuna_suggest(cls, trial, prefix: str = ""):
        """
        Mock optuna_suggest method. Returns the current _optuna_suggest_return_value.
        """
        if cls._optuna_suggest_return_value is None:
            raise NotImplementedError(
                f"{cls.__name__}.optuna_suggest() must be implemented to use Optuna."
            )
        return cls._optuna_suggest_return_value

    def update_allocate_return_value(self, value: pd.DataFrame):
        """
        Update the return value for the allocate method.

        :param value: The DataFrame to return when allocate is called.
        """
        self._allocate_return_value = value

    def allocate(
        self, signals: pd.DataFrame = None, returns: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Given signals and/or returns, produce a DataFrame of portfolio weights over time.
        Always returns a valid DataFrame by default for testing.
        """
        import pandas as pd

        if self._allocate_return_value is not None:
            return self._allocate_return_value
        # Default fallback: single symbol, single weight
        return pd.DataFrame({"AAPL": [1.0]})


def mockPortfolioStrategy():
    """
    Create and return an instance of MockPortfolioStrategy.

    :return: An instance of MockPortfolioStrategy.
    """
    return MockPortfolioStrategy()
