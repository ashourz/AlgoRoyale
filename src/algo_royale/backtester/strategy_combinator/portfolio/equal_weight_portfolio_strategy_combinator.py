from algo_royale.backtester.strategy.portfolio.equal_weight_portfolio_strategy import (
    EqualWeightPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class EqualWeightPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=EqualWeightPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
