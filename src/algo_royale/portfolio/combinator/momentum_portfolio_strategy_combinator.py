from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.momentum_portfolio_strategy import (
    MomentumPortfolioStrategy,
)


class MomentumPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(MomentumPortfolioStrategy)
