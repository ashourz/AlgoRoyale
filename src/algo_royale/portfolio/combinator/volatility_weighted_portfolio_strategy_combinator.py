from algo_royale.backtester.strategy.portfolio.volatility_weighted_portfolio_strategy import (
    VolatilityWeightedPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class VolatilityWeightedPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = VolatilityWeightedPortfolioStrategy
