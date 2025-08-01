from algo_royale.backtester.maps.condition_class_map import CONDITION_CLASS_MAP
from algo_royale.backtester.maps.stateful_logic_map import STATEFUL_LOGIC_CLASS_MAP
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.logging.loggable import Loggable


class StrategyFactory:
    """Factory for creating signal strategies based on provided parameters.
    This factory allows for dynamic instantiation of strategies with their conditions
    and stateful logic based on configuration parameters.

    Parameters:
        logger (Logger): Logger instance for logging messages.
        strategy_logger (Logger): Logger instance for strategy-specific logging.
    """

    def __init__(self, logger: Loggable, strategy_logger: Loggable):
        self.logger = logger
        self.strategy_logger = strategy_logger

    def instantiate_conditions(self, cond_list, debug: bool = False):
        """Convert a list of dicts to a list of condition objects."""
        if not cond_list:
            return []
        return [
            CONDITION_CLASS_MAP[cond_class](logger=self.strategy_logger, **params)
            for cond in cond_list
            for cond_class, params in cond.items()
        ]

    def instantiate_stateful_logic(self, logic):
        """Convert a dict to a stateful logic object, or return None.
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
            return cls(logger=self.strategy_logger, **params)
        raise ValueError(f"Unsupported logic format: {logic}")

    def build_strategy(self, strategy_class, params: dict) -> BaseSignalStrategy:
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
                params[key] = self.instantiate_conditions(cond_list=params[key])

        # Convert stateful_logic dict to object, if present
        if "stateful_logic" in params and params["stateful_logic"] is not None:
            params["stateful_logic"] = self.instantiate_stateful_logic(
                logic=params["stateful_logic"]
            )

        return strategy_class(logger=self.strategy_logger, **params)
