from .base_column_names import BaseColumnNames


class PortfolioEvaluationKeys(BaseColumnNames):
    """Keys used in the output dictionary from portfolio backtest evaluation."""

    TOTAL_RETURN = "total_return"
    MEAN_RETURN = "mean_return"
    VOLATILITY = "volatility"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    NUM_TRADES = "num_trades"
    # Add more as needed
