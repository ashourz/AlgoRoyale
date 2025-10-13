# src/models/alpaca_models/alpaca_bar.py

from typing import Any, Dict

from pydantic import RootModel


class ConditionCodeMap(RootModel[Dict[str, str]]):
    """
    A model that maps trade condition codes (single-character keys) to their descriptions.

    Typically used to interpret condition codes returned by the Alpaca API when querying trade data.
    """

    def describe(self, code: str) -> str:
        """
        Retrieve the description for a given condition code.

        Args:
            code (str): The condition code to describe.

        Returns:
            str: The human-readable description of the condition code.
                 Returns 'Unknown condition code' if the code is not found.
        """
        return self.root.get(code, "Unknown condition code")

    @classmethod
    def from_raw(cls, raw_data: Dict[str, Any]) -> "ConditionCodeMap":
        """
        Create a ConditionCodeMap instance from raw dictionary data.

        This is useful when parsing responses directly from the Alpaca API.

        Args:
            raw_data (Dict[str, Any]): A dictionary where each key is a condition code (str)
                                       and each value is its description (str).

        Returns:
            ConditionCodeMap: A new instance of the model.
        """
        return cls.parse_obj(raw_data)
