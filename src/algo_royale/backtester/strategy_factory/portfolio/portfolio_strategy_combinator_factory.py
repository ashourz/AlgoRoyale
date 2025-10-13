import os

from algo_royale.backtester.maps.portfolio_strategy_combinator_map import (
    PORTFOLIO_STRATEGY_COMBINATOR_MAP,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class PortfolioStrategyCombinatorFactory:
    """
    Factory class for creating portfolio strategy combinators.
    """

    def __init__(
        self, combinator_list_path: str, logger: Loggable, strategy_logger: Loggable
    ):
        self.logger = logger
        self.strategy_logger = strategy_logger
        self.combinator_list_path = combinator_list_path
        if not os.path.exists(combinator_list_path):
            self.logger.error(
                f"Combinator list file does not exist at: {combinator_list_path}"
            )
            raise FileNotFoundError(
                f"Combinator list file not found at: {combinator_list_path}"
            )

    def all_combinators(self) -> list[PortfolioStrategyCombinator]:
        """
        Return a list of all available portfolio strategy combinators.
        """
        class_names = self._load_combinators_class_names()
        combinators: list[PortfolioStrategyCombinator] = []
        for class_name in class_names:
            if class_name in PORTFOLIO_STRATEGY_COMBINATOR_MAP:
                combinator_class = PORTFOLIO_STRATEGY_COMBINATOR_MAP[class_name]
                if issubclass(combinator_class, PortfolioStrategyCombinator):
                    instance = combinator_class(
                        strategy_logger=self.strategy_logger,
                        logger=self.logger,
                    )
                    combinators.append(instance)
                else:
                    self.logger.error(
                        f"Class {class_name} is not a subclass of PortfolioStrategyCombinator."
                    )
            else:
                self.logger.error(
                    f"Class {class_name} not found in PORTFOLIO_STRATEGY_COMBINATOR_MAP."
                )
        if not combinators:
            self.logger.error("No valid portfolio strategy combinators found.")
            raise ValueError("No valid portfolio strategy combinators found.")
        return combinators

    def _load_combinators_class_names(self) -> list[type[PortfolioStrategyCombinator]]:
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
