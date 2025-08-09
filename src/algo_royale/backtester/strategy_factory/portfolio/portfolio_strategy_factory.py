from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


class PortfolioStrategyFactory:
    def __init__(
        self, asset_matrix_preparer, logger: Loggable, strategy_logger: Loggable
    ):
        """
        Initialize the PortfolioStrategyFactory with a strategy and asset matrix preparer.

        :param strategy: The portfolio strategy to be used.
        :param asset_matrix_preparer: The preparer for the asset matrix.
        :param window_size: The size of the buffer window.
        """
        self.asset_matrix_preparer = asset_matrix_preparer
        self.logger = logger
        self.strategy_logger = strategy_logger

    def build_strategy(
        self, strategy_class: type[BasePortfolioStrategy], params: dict
    ) -> BasePortfolioStrategy:
        """
        Build a new instance of the portfolio strategy.
        """
        try:
            params = dict(params)  # Ensure we have a mutable copy
            return strategy_class(logger=self.strategy_logger, **params)
        except Exception as e:
            self.logger.error(f"Error building strategy: {e}")
            return None

    def build_buffered_strategy(
        self, strategy_class: type[BasePortfolioStrategy], params: dict
    ) -> BasePortfolioStrategy | None:
        """
        Build a new instance of the buffered portfolio strategy.
        """
        try:
            strategy = self.build_strategy(strategy_class, params)
            if not strategy:
                self.logger.error("Failed to build strategy")
                return None
            return BufferedPortfolioStrategy(
                strategy=strategy,
                asset_matrix_preparer=self.asset_matrix_preparer,
                logger=self.strategy_logger,
            )
        except Exception as e:
            self.logger.error(f"Error building buffered strategy: {e}")
            return None
