import pandas as pd


class MockStrategyCondition:
    """
    Mock implementation of a strategy condition for testing purposes.
    This class simulates the behavior of a strategy condition component.
    """

    def __init__(self):
        """
        Initialize the mock strategy condition with a unique identifier.

        :param hash_id: A unique identifier for the strategy condition.
        """
        self.required_columns = set()
        self.default_description = "Mock strategy condition for testing purposes."
        self.description = self.default_description
        self.default_id = "mock_strategy_condition"
        self.id = self.default_id

    def reset(self):
        """
        Reset the strategy condition to its initial state.
        """
        self.required_columns = set()
        self.all_possible_conditions = []
        self.description = self.default_description
        self.id = self.default_id
        self._call_return_value = None  # Reset call return value

    def get_id(self) -> str:
        """
        Get the unique identifier for the strategy condition.

        :return: A unique identifier for the strategy condition.
        """
        return self.id

    def set_id(self, id: str):
        """
        Set a new unique identifier for the strategy condition.

        :param hash_id: A new unique identifier for the strategy condition.
        """
        self.id = id

    def required_columns(self) -> set[str]:
        """
        Return the required columns for this strategy condition.

        :return: A set of required columns.
        """
        return self.required_columns

    def update_required_columns(self, columns: list[str]):
        """
        Update the required columns for this strategy condition.

        :param columns: A list of required columns.
        """
        self.required_columns = set(columns)

    @classmethod
    def update_all_possible_conditions(cls, conditions: list):
        """
        Update the list of all possible conditions for this strategy condition.

        :param conditions: A list of conditions to set.
        """
        cls.all_possible_conditions = conditions

    @classmethod
    def all_possible_conditions(cls):
        """
        Returns all possible instances of this condition class with different parameter combinations.
        If no parameters are defined, returns a single instance of the class.
        """
        if cls.all_possible_conditions is None:
            return [cls()]
        return cls.all_possible_conditions

    @classmethod
    def update_available_param_grid(cls, param_grid: dict):
        """
        Update the available parameter grid for this strategy condition.

        :param param_grid: A dictionary of parameter names to lists of possible values.
        """
        cls.available_param_grid = param_grid

    @classmethod
    def available_param_grid(cls) -> dict:
        """
        Returns a dictionary of parameter names to lists of possible values.
        This should be overridden in subclasses to provide specific parameter grids.

        :return: A dictionary of parameter names to lists of possible values.
        """
        if cls.available_param_grid is None:
            return {}
        return cls.available_param_grid

    @classmethod
    def optuna_suggest(cls, trial, prefix=""):
        """
        Mock optuna_suggest method. Returns the current _optuna_suggest_return_value.

        :param trial: The Optuna trial object.
        :param prefix: Optional prefix for parameter names.
        :return: An instance of the mock strategy condition.
        """
        if cls.optuna_suggest_return_value is None:
            raise ValueError("optuna_suggest_return_value is not set.")
        return cls.optuna_suggest_return_value

    @classmethod
    def set_optuna_suggest_return_value(cls, value: "MockStrategyCondition"):
        """
        Update the return value for optuna_suggest.

        :param value: The value to return when optuna_suggest is invoked.
        """
        cls.optuna_suggest_return_value = value

    def __call__(self, *args, **kwargs):
        """
        Mock call method. Returns the current _call_return_value.
        """
        if self._call_return_value is None:
            raise ValueError(
                "Call return value is not set. Use set_call_return_value() to set it."
            )
        return self._call_return_value

    def set_call_return_value(self, value: pd.Series):
        """
        Update the return value for __call__.

        :param value: The value to return when __call__ is invoked.
        """
        self._call_return_value = value
