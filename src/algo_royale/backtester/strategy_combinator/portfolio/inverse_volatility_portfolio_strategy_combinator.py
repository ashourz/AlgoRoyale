from algo_royale.backtester.strategy.portfolio.inverse_volatility_portfolio_strategy import (
    InverseVolatilityPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class InverseVolatilityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = InverseVolatilityPortfolioStrategy
