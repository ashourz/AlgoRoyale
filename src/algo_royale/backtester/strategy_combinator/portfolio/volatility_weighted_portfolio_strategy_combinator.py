from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.volatility_weighted_portfolio_strategy import (
    VolatilityWeightedPortfolioStrategy,
)


class VolatilityWeightedPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = VolatilityWeightedPortfolioStrategy
