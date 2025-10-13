from algo_royale.backtester.strategy.portfolio.inverse_volatility_portfolio_strategy import (
    InverseVolatilityPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class InverseVolatilityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=InverseVolatilityPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
