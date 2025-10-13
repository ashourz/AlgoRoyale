from algo_royale.backtester.strategy.portfolio.winner_takes_all_portfolio_strategy import (
    WinnerTakesAllPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class WinnerTakesAllPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=WinnerTakesAllPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
