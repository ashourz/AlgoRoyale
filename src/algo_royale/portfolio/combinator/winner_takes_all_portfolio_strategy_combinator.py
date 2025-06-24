from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.winner_takes_all_portfolio_strategy import (
    WinnerTakesAllPortfolioStrategy,
)


class WinnerTakesAllPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = WinnerTakesAllPortfolioStrategy
