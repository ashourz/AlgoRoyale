import json
import threading
from logging import Logger
from typing import Callable, Optional, Sequence

from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.maps.condition_class_map import CONDITION_CLASS_MAP
from algo_royale.strategy_factory.maps.stateful_logic_map import (
    STATEFUL_LOGIC_CLASS_MAP,
)
from algo_royale.strategy_factory.strategies.base_signal_strategy import (
    BaseSignalStrategy,
)


##TODO: THERE IS LITTLE NEED FOR THIS CLASS AND SHOULD BE TRANSITIONED OUT
class StrategyFactory:
    """
    Factory class to manage and generate strategy combinations.
    This class is responsible for loading strategy definitions, generating all possible
    strategy combinations, and saving a mapping of strategies to their descriptions.
    It uses various strategy combinators to create complex strategies based on simple ones.
    The strategy combinations can be used for backtesting or live trading.
    Parameters:
        strategy_map_path (str): Path to save the strategy map JSON file.
        logger (Logger): Logger instance for logging messages.
        strategy_combinators (Optional[list[type[StrategyCombinator]]]): List of strategy combinators to use.
    """

    def __init__(
        self,
        strategy_map_path: str,
        strategy_combinators: Sequence[type[SignalStrategyCombinator]],
        logger: Logger,
    ):
        self.strategy_combinators = strategy_combinators
        self._all_strategy_combinations: Optional[list[BaseSignalStrategy]] = None
        self.logger = logger
        self.strategy_map_path = strategy_map_path
        self._strategy_map_lock = threading.Lock()

    def get_all_strategy_combination_lambdas(
        self,
    ) -> list[Callable[[], list[BaseSignalStrategy]]]:
        """
        Returns a list of callables, each of which generates all strategies for a combinator,
        saves them to the strategy map, and returns the list.
        """
        self.logger.info(
            "Generating all strategy combinations. Strategy combinator count: %d",
            len(self.strategy_combinators) if self.strategy_combinators else 0,
        )
        combination_lambdas = []

        for combinator in self.strategy_combinators:
            if issubclass(combinator, SignalStrategyCombinator):
                self.logger.info("Using strategy combinator: %s", combinator.__name__)

                def make_lambda(c=combinator):
                    def generate_and_save():
                        all_strategies = [
                            s_lambda()
                            for s_lambda in c.all_strategy_combinations(
                                logger=self.logger
                            )
                        ]
                        self._save_strategy_map(all_strategies)
                        return all_strategies

                    return generate_and_save

                combination_lambdas.append(make_lambda())
            else:
                self.logger.warning(
                    "Provided combinator %s is not a subclass of StrategyCombinator. Skipping.",
                    combinator.__name__,
                )
        if not combination_lambdas:
            self.logger.warning(
                "No valid strategy combinators provided. Returning empty list."
            )
            return []

        return combination_lambdas

    def _save_strategy_map(self, strategies: list[BaseSignalStrategy]) -> None:
        """
        Generates and saves a mapping of {strategy_class: {hash_id: description}}
        to the path specified by self.strategy_map_path.
        """
        with self._strategy_map_lock:  # <-- Lock for thread safety
            self.logger.info("Saving strategy map to %s", self.strategy_map_path)
            strategy_id_map = {}
            for strat in strategies:
                class_name = strat.__class__.__name__
                hash_id = strat.get_hash_id()
                desc = strat.get_description()
                if class_name not in strategy_id_map:
                    strategy_id_map[class_name] = {}
                strategy_id_map[class_name][hash_id] = desc

            with open(self.strategy_map_path, "w") as f:
                json.dump(strategy_id_map, f, indent=2)

            self.logger.info(
                "Strategy map saved successfully with %d strategies.", len(strategies)
            )

    @staticmethod
    def instantiate_conditions(cond_list):
        """Convert a list of dicts to a list of condition objects."""
        if not cond_list:
            return []
        return [
            CONDITION_CLASS_MAP[cond_class](**params)
            for cond in cond_list
            for cond_class, params in cond.items()
        ]

    @staticmethod
    def instantiate_stateful_logic(logic):
        """
        Convert a dict to a stateful logic object, or return None.
        Accepts:
            - None: returns None
            - dict: {"ClassName": {"params": ...}}
        """
        if not logic:
            return None
        if isinstance(logic, dict):
            # There should only be one key
            class_name, params = next(iter(logic.items()))
            cls = STATEFUL_LOGIC_CLASS_MAP[class_name]
            return cls(**params)
        raise ValueError(f"Unsupported logic format: {logic}")

    @classmethod
    def build_strategy(cls, strategy_class, params: dict):
        """
        Given a strategy class and params (with *_conditions as lists of dicts),
        returns an initialized strategy with all condition objects.
        """
        params = dict(params)  # shallow copy

        # Convert *_conditions lists of dicts to lists of condition objects
        for key in [
            "entry_conditions",
            "exit_conditions",
            "trend_conditions",
            "filter_conditions",
        ]:
            if key in params and isinstance(params[key], list):
                params[key] = cls.instantiate_conditions(params[key])

        # Convert stateful_logic dict to object, if present
        if "stateful_logic" in params and params["stateful_logic"] is not None:
            params["stateful_logic"] = cls.instantiate_stateful_logic(
                params["stateful_logic"]
            )

        return strategy_class(**params)
