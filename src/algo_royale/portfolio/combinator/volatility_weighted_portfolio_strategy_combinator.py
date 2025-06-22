from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.volatility_weighted_portfolio_strategy import (
    VolatilityWeightedPortfolioStrategy,
)


class VolatilityWeightedPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(VolatilityWeightedPortfolioStrategy)
