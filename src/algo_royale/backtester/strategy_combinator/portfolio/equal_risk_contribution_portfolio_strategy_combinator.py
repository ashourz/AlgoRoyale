from algo_royale.backtester.strategy.portfolio.equal_risk_contribution_portfolio_strategy import (
    EqualRiskContributionPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class EqualRiskContributionPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self, strategy_logger: Loggable, logger: Loggable):
        super().__init__(
            strategy_class=EqualRiskContributionPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )
