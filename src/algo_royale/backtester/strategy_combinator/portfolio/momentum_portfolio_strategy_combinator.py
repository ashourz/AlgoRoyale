from algo_royale.backtester.strategy.portfolio.momentum_portfolio_strategy import (
    MomentumPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class MomentumPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=MomentumPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
