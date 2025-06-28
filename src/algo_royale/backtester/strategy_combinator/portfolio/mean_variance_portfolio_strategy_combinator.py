from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.mean_variance_portfolio_strategy import (
    MeanVariancePortfolioStrategy,
)


class MeanVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MeanVariancePortfolioStrategy
