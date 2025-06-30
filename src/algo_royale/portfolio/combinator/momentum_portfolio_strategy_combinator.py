from algo_royale.backtester.strategy.portfolio.momentum_portfolio_strategy import (
    MomentumPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class MomentumPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MomentumPortfolioStrategy
