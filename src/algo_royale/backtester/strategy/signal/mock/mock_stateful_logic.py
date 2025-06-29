from typing import Any


class MockStatefulLogic:
    """
    Mock implementation of a stateful logic for testing purposes.
    This class simulates the behavior of a stateful logic component.
    """

    def __init__(self, hash_id: str):
        """
        Initialize the mock stateful logic with a unique identifier.

        :param hash_id: A unique identifier for the stateful logic.
        """
        self.hash_id = hash_id
        self.required_columns = set()
        self.default_description = "Mock stateful logic for testing purposes."
        self.description = self.default_description
        self.default_id = "mock_stateful_logic"
        self.id = self.default_id
        self._call_return_signal = None  # Placeholder for the signal return value
        self._call_return_info_dic = (
            None  # Placeholder for the info dictionary return value
        )
        self._call_return_value = (None, None)  # Default return value for __call__

    def reset(self):
        """
        Reset the stateful logic to its initial state.
        This includes resetting the hash_id, required_columns,
        all_possible_conditions, description, and id.
        """
        self.required_columns = set()
        self.description = self.default_description
        self.id = self.default_id
        self._call_return_value = (None, None)  # Reset call return value

    def required_columns(self) -> set[str]:
        """
        Return the required columns for this stateful logic.

        :return: A set of required columns.
        """
        return self.required_columns

    def update_required_columns(self, columns: list[str]):
        """
        Update the required columns for this stateful logic.

        :param columns: A list of required columns.
        """
        self.required_columns = set(columns)

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
    def update_available_param_grid(cls, param_grid: dict):
        """
        Update the available parameter grid for this stateful logic.

        :param param_grid: A dictionary of parameter names to lists of possible values.
        """
        cls.available_param_grid = param_grid

    @classmethod
    def all_possible_conditions(cls):
        """
        Returns a list of all possible condition instances for this class,
        using the available_param_grid.
        """
        if cls.all_possible_conditions is None:
            return [cls()]
        return cls.all_possible_conditions

    @classmethod
    def update_all_possible_conditions(cls, conditions: list):
        """
        Update the list of all possible conditions for this stateful logic.

        :param conditions: A list of condition instances.
        """
        cls.all_possible_conditions = conditions

    def get_id(self):
        """
        Returns a unique string identifier for this stateful logic instance,
        including the class name and its parameters.
        """
        return self.id

    def update_id(self, new_id: str):
        """
        Update the unique identifier for this stateful logic instance.

        :param new_id: A new unique identifier for the stateful logic.
        """
        self.id = new_id

    def __call__(self, *args, **kwargs):
        """
        Mock call method. Returns the current _call_return_value.
        """
        return self._call_return_value

    def set_call_return_value(self, signal: Any, info_dic=dict):
        """
        Update the return value for __call__.
        :param value: The value to return when __call__ is invoked.
        """
        self._call_return_value = (signal, info_dic)

    @classmethod
    def optuna_suggest(cls, trial, prefix=""):
        """
        Mock optuna_suggest method. Returns the current _optuna_suggest_return_value.
        """
        if hasattr(cls, "_optuna_suggest_return_value"):
            return cls._optuna_suggest_return_value
        return None

    @classmethod
    def set_optuna_suggest_return_value(cls, value):
        """
        Set a custom return value for optuna_suggest for this mock class.
        :param value: The value to return from optuna_suggest.
        """
        cls._optuna_suggest_return_value = value
