from algo_royale.backtester.strategy.portfolio.minimum_variance_portfolio_strategy import (
    MinimumVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class MinimumVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MinimumVariancePortfolioStrategy
