from algo_royale.backtester.strategy.portfolio.mean_variance_portfolio_strategy import (
    MeanVariancePortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class MeanVariancePortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=MeanVariancePortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
