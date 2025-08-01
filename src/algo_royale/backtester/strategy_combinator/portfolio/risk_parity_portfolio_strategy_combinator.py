from algo_royale.backtester.strategy.portfolio.risk_parity_portfolio_strategy import (
    RiskParityPortfolioStrategy,
)
from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class RiskParityPortfolioStrategyCombinator(PortfolioStrategyCombinator):
    def __init__(
        self,
        strategy_logger: Loggable = None,
        logger: Loggable = None,
    ):
        super().__init__(
            strategy_class=RiskParityPortfolioStrategy,
            strategy_logger=strategy_logger,
            logger=logger,
        )

    """Combines conditions and logic for a Risk Parity portfolio strategy.
    This strategy focuses on balancing risk across different assets in the portfolio.
    It does not include any filter conditions or trend conditions, focusing solely on the risk parity logic.
    """
