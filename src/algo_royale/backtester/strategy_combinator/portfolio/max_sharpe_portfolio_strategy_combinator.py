from algo_royale.backtester.strategy.portfolio.max_sharpe_portfolio_strategy import (
    MaxSharpePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class MaxSharpePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=MaxSharpePortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
