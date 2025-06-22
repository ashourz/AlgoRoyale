from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.equal_risk_contribution_portfolio_strategy import (
    EqualRiskContributionPortfolioStrategy,
)


class EqualRiskContributionPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(EqualRiskContributionPortfolioStrategy)
