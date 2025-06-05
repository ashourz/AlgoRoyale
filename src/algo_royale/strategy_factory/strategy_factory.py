import json
from logging import Logger
from typing import Optional

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

    def get_all_strategy_combinations(self):
        """
        Returns all strategy combinations across all symbols.
        This method caches the result to avoid recomputing.
        If the strategy combinations have already been computed, it returns the cached value."""
        if self._all_strategy_combinations is not None:
            return self._all_strategy_combinations
        all_strategies = self._get_all_strategy_combinations()
        self._save_strategy_map(all_strategies)
        self._all_strategy_combinations = all_strategies
        return self._all_strategy_combinations

    def _get_all_strategy_combinations(self) -> list[Strategy]:
        """
        Returns all strategy combinations across all symbols.
        This method is useful for testing or analysis purposes.
        """
        all_strategies: list[Strategy] = []
        self.logger.info(
            "Generating all strategy combinations. Strategy combinator count: %d",
            len(self.strategy_combinators) if self.strategy_combinators else 0,
        )
        for combinator in self.strategy_combinators:
            if issubclass(combinator, StrategyCombinator):
                all_strategies.extend(
                    combinator.all_strategy_combinations(logger=self.logger)
                )
        self.logger.info(
            "Generated %d strategy combinations from combinators.", len(all_strategies)
        )
        return all_strategies

    def _save_strategy_map(self, strategies: list[Strategy]) -> None:
        """
        Generates and saves a mapping of {strategy_class: {hash_id: description}}
        to the path specified by self.strategy_map_path.
        """
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
