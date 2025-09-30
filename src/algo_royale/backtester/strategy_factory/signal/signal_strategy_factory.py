from typing import Optional

from algo_royale.backtester.maps.condition_class_map import CONDITION_CLASS_MAP
from algo_royale.backtester.maps.stateful_logic_map import STATEFUL_LOGIC_CLASS_MAP
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_condition import (
    BufferedStrategyCondition,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_signal_strategy import (
    BufferedSignalStrategy,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_stateful_logic import (
    BufferedStatefulLogic,
)
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.logging.loggable import Loggable


class SignalStrategyFactory:
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

    def instantiate_conditions(self, cond_list) -> list[BaseSignalStrategy]:
        """Convert a list of dicts to a list of condition objects."""
        if not cond_list:
            return []
        return [
            CONDITION_CLASS_MAP[cond_class](logger=self.strategy_logger, **params)
            for cond in cond_list
            for cond_class, params in cond.items()
        ]

    def instantiate_buffered_conditions(
        self, cond_list
    ) -> list[BufferedStrategyCondition]:
        """Convert a list of dicts to a list of BufferedStrategyCondition objects."""
        try:
            std_conditions = self.instantiate_conditions(cond_list)
            if not std_conditions:
                return []
            # Wrap each condition in a BufferedSignalStrategy if not already wrapped
            buffered_conditions = []
            for i, cond in enumerate(std_conditions):
                if isinstance(cond, BufferedStrategyCondition):
                    # If already buffered, just append it
                    buffered_conditions.append(cond)
                elif isinstance(cond, StrategyCondition):
                    # Wrap each condition in a BufferedStrategyCondition
                    buffered_conditions.append(
                        BufferedStrategyCondition(
                            condition=cond,
                            window_size=cond.window_size,
                            logger=self.strategy_logger,
                        )
                    )
            return buffered_conditions
        except Exception as e:
            self.logger.error(
                f"Error instantiating buffered conditions: {e}. "
                + "Ensure all conditions have a valid window_size."
            )
            return []

    def instantiate_stateful_logic(self, logic) -> Optional[StatefulLogic]:
        """Convert a dict to a stateful logic object, or return None.
        Accepts:
            - None: returns None
            - dict: {"ClassName": {"params": ...}}
        """
        try:
            if not logic:
                return None
            if isinstance(logic, dict):
                # There should only be one key
                class_name, params = next(iter(logic.items()))
                cls = STATEFUL_LOGIC_CLASS_MAP[class_name]
                return cls(logger=self.strategy_logger, **params)
            else:
                self.logger.error(
                    f"Unsupported logic format: {logic}. Expected dict with class name as key."
                )
                return None
        except Exception as e:
            self.logger.error(
                f"Error instantiating stateful logic: {e}. "
                + "Ensure the logic is a valid dict with a single class name key."
            )
            return None

    def instantiate_buffered_stateful_logic(
        self, logic
    ) -> Optional[BufferedStatefulLogic]:
        """Convert a dict to a BufferedStatefulLogic object, or return None.
        Accepts:
            - None: returns None
            - dict: {"ClassName": {"params": ...}}
        """
        try:
            std_logic = self.instantiate_stateful_logic(logic)
            if not std_logic:
                return None
            # Wrap the standard stateful logic in a BufferedStatefulLogic
            if isinstance(std_logic, BufferedStatefulLogic):
                return std_logic
            elif isinstance(std_logic, StatefulLogic):
                return BufferedStatefulLogic(
                    stateful_logic=std_logic,
                    window_size=std_logic.window_size,
                    logger=self.strategy_logger,
                )
        except Exception as e:
            self.logger.error(
                f"Error instantiating buffered stateful logic: {e}. "
                + "Ensure the logic is a valid dict with a single class name key."
            )
            return None

    def build_strategy(
        self, strategy_class: type[BaseSignalStrategy], params: dict
    ) -> BaseSignalStrategy:
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

    def build_buffered_strategy(
        self, strategy_class: type[BaseSignalStrategy], params: dict
    ) -> BufferedSignalStrategy:
        """
        Given a base strategy class and corresponding params (with *_conditions as lists of dicts),
        returns an initialized buffered strategy with all condition objects.
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
                params[key] = self.instantiate_buffered_conditions(
                    cond_list=params[key]
                )

        # Convert stateful_logic dict to object, if present
        if "stateful_logic" in params and params["stateful_logic"] is not None:
            params["stateful_logic"] = self.instantiate_buffered_stateful_logic(
                logic=params["stateful_logic"]
            )

        return BufferedSignalStrategy(
            strategy_type=strategy_class, logger=self.strategy_logger, **params
        )
