from algo_royale.backtester.strategy.portfolio.minimum_variance_portfolio_strategy import (
    MinimumVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class MinimumVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=MinimumVariancePortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
