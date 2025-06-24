from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.max_sharpe_portfolio_strategy import (
    MaxSharpePortfolioStrategy,
)


class MaxSharpePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MaxSharpePortfolioStrategy
