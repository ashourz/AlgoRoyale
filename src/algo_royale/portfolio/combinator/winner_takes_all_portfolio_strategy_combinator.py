from algo_royale.backtester.strategy.portfolio.winner_takes_all_portfolio_strategy import (
    WinnerTakesAllPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class WinnerTakesAllPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = WinnerTakesAllPortfolioStrategy
