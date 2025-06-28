from algo_royale.backtester.strategy.portfolio.equal_weight_portfolio_strategy import (
    EqualWeightPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class EqualWeightPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = EqualWeightPortfolioStrategy
