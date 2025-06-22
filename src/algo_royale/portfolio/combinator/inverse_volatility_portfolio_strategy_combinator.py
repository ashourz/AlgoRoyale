from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.portfolio.strategies.inverse_volatility_portfolio_strategy import (
    InverseVolatilityPortfolioStrategy,
)


class InverseVolatilityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(self):
        super().__init__(InverseVolatilityPortfolioStrategy)
