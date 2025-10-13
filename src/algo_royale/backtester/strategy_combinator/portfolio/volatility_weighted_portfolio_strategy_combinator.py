from algo_royale.backtester.strategy.portfolio.volatility_weighted_portfolio_strategy import (
    VolatilityWeightedPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class VolatilityWeightedPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=VolatilityWeightedPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
