from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.minimum_variance_portfolio_strategy import (
    MinimumVariancePortfolioStrategy,
)


class MinimumVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(MinimumVariancePortfolioStrategy)
