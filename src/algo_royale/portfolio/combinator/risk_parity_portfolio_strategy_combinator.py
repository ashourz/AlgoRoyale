from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.risk_parity_portfolio_strategy import (
    RiskParityPortfolioStrategy,
)


class RiskParityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = RiskParityPortfolioStrategy
