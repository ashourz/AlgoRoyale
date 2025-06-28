from algo_royale.backtester.strategy.portfolio.equal_risk_contribution_portfolio_strategy import (
    EqualRiskContributionPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class EqualRiskContributionPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = EqualRiskContributionPortfolioStrategy
