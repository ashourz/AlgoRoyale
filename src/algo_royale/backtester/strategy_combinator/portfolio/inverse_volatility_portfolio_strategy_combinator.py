from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.inverse_volatility_portfolio_strategy import (
    InverseVolatilityPortfolioStrategy,
)


class InverseVolatilityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    strategy_class = InverseVolatilityPortfolioStrategy
