import os

from algo_royale.backtester.maps.signal_strategy_combinator_map import (
    SIGNAL_STRATEGY_COMBINATOR_MAP,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class SignalStrategyCombinatorFactory:
    """
    Factory class for creating signal strategy combinators.
    """

    def __init__(self, combinator_list_path: str, logger: Loggable):
        self.logger = logger
        self.combinator_list_path = combinator_list_path
        if not os.path.exists(combinator_list_path):
            self.logger.error(
                f"Combinator list file does not exist at: {combinator_list_path}"
            )
            raise FileNotFoundError(
                f"Combinator list file not found at: {combinator_list_path}"
            )

    def all_combinators(self) -> list[SignalStrategyCombinator]:
        """
        Return a list of all available signal strategy combinators.
        """
        class_names = self._load_combinators_class_names()
        combinators = []
        for class_name in class_names:
            if class_name in SIGNAL_STRATEGY_COMBINATOR_MAP:
                combinator_class = SIGNAL_STRATEGY_COMBINATOR_MAP[class_name]
                if issubclass(combinator_class, SignalStrategyCombinator):
                    instance = combinator_class()
                    combinators.append(instance)
                else:
                    self.logger.error(
                        f"Class {class_name} is not a subclass of SignalStrategyCombinator."
                    )
            else:
                self.logger.error(
                    f"Class {class_name} not found in SIGNAL_STRATEGY_COMBINATOR_MAP."
                )
        if not combinators:
            self.logger.error("No valid signal strategy combinators found.")
            raise ValueError("No valid signal strategy combinators found.")
        return combinators

    def _load_combinators_class_names(self) -> list[type[SignalStrategyCombinator]]:
        """
        Load and return a list of strategy combinators from the specified path.
        """
        try:
            if not os.path.exists(self.combinator_list_path):
                self.logger.error(
                    f"Combinator list file does not exist at: {self.combinator_list_path}"
                )
                raise FileNotFoundError(
                    f"Combinator list file not found at: {self.combinator_list_path}"
                )
            with open(self.combinator_list_path, "r") as f:
                combinator_list = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]  # Read each line as a separate symbol

        except FileNotFoundError:
            self.logger.error(
                f"Combinator list file not found: {self.combinator_list_path}"
            )
        except Exception as e:
            self.logger.error(f"Error loading combinators: {e}")

        return combinator_list
