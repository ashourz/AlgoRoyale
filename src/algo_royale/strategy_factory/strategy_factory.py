import json
import threading
from logging import Logger
from typing import Callable, Optional

from algo_royale.config.config import Config
from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class StrategyFactory:
    """
    Factory class to manage and generate strategy combinations.
    This class is responsible for loading strategy definitions, generating all possible
    strategy combinations, and saving a mapping of strategies to their descriptions.
    It uses various strategy combinators to create complex strategies based on simple ones.
    The strategy combinations can be used for backtesting or live trading.
    Parameters:
        config (Config): Configuration object containing paths and settings.
        strategy_combinators (Optional[list[type[StrategyCombinator]]]): List of strategy combinators to use.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        strategy_combinators: Optional[list[type[StrategyCombinator]]] = None,
    ):
        self.strategy_map_path = config.get("paths.backtester", "strategy_map_path")
        self.strategy_combinators = strategy_combinators
        self._all_strategy_combinations: Optional[list[Strategy]] = None
        self.logger = logger
        self._strategy_map_lock = threading.Lock()

    def get_all_strategy_combination_lambdas(
        self,
    ) -> list[Callable[[], list[Strategy]]]:
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
            if issubclass(combinator, StrategyCombinator):
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

    def _save_strategy_map(self, strategies: list[Strategy]) -> None:
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
