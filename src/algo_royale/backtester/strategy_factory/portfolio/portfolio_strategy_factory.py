import json
import threading
from logging import Logger
from typing import Callable, Optional, Sequence

from src.algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from src.algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class PortfolioStrategyFactory:
    def __init__(
        self,
        strategy_map_path: str,
        strategy_combinators: Sequence[type[PortfolioStrategyCombinator]],
        logger: Logger,
    ):
        self.strategy_combinators = strategy_combinators
        self._all_strategy_combinations: Optional[list[BasePortfolioStrategy]] = None
        self.logger = logger
        self.strategy_map_path = strategy_map_path
        self._strategy_map_lock = threading.Lock()

    def get_all_strategy_combination_lambdas(
        self,
    ) -> list[Callable[[], list[BasePortfolioStrategy]]]:
        self.logger.info(
            "Generating all portfolio strategy combinations. Combinator count: %d",
            len(self.strategy_combinators) if self.strategy_combinators else 0,
        )
        combination_lambdas = []

        for combinator in self.strategy_combinators:
            if issubclass(combinator, PortfolioStrategyCombinator):
                self.logger.info(
                    "Using portfolio strategy combinator: %s", combinator.__name__
                )

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
                    "Provided combinator %s is not a subclass of PortfolioStrategyCombinator. Skipping.",
                    combinator.__name__,
                )
        if not combination_lambdas:
            self.logger.warning(
                "No valid portfolio strategy combinators provided. Returning empty list."
            )
            return []

        return combination_lambdas

    def _save_strategy_map(self, strategies: list[BasePortfolioStrategy]) -> None:
        with self._strategy_map_lock:
            self.logger.info(
                "Saving portfolio strategy map to %s", self.strategy_map_path
            )
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
                "Portfolio strategy map saved successfully with %d strategies.",
                len(strategies),
            )
