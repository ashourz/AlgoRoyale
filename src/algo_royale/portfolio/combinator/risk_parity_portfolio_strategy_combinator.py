from algo_royale.backtester.strategy.portfolio.risk_parity_portfolio_strategy import (
    RiskParityPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class RiskParityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = RiskParityPortfolioStrategy
