from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.equal_weight_portfolio_strategy import (
    EqualWeightPortfolioStrategy,
)


class EqualWeightPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = EqualWeightPortfolioStrategy
