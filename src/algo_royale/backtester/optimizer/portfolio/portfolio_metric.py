from enum import Enum


class PortfolioMetric(Enum):
    TOTAL_RETURN = "total_return"
    MAX_DRAWDOWN = "max_drawdown"
    SHARPE_RATIO = "sharpe_ratio"
    # Add more as needed
