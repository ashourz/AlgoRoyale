from algo_royale.backtester.strategy.portfolio.max_sharpe_portfolio_strategy import (
    MaxSharpePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class MaxSharpePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = MaxSharpePortfolioStrategy
