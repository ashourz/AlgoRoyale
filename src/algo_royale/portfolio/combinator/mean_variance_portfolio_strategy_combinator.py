from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.mean_variance_portfolio_strategy import (
    MeanVariancePortfolioStrategy,
)


class MeanVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(MeanVariancePortfolioStrategy)
