from algo_royale.backtester.strategy.portfolio.mean_variance_portfolio_strategy import (
    MeanVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class MeanVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MeanVariancePortfolioStrategy
