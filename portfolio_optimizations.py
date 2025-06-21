"""
portfolio_optimizations.py

Script to run portfolio strategy optimizations for multiple metrics and save results for later analysis/visualization.
"""

import json
import logging
from pathlib import Path

from algo_royale.portfolio.portfolio_strategy.portfolio_strategy_optimizer import (
    OptimizationDirection,
    PortfolioMetric,
    PortfolioStrategyOptimizer,
)

# from algo_royale.portfolio.portfolio_strategy.your_strategy import YourStrategyClass
# from your_backtest_module import your_backtest_fn

# Example placeholders (replace with your actual strategy and backtest function)
YourStrategyClass = None  # TODO: import your strategy class


def your_backtest_fn(strategy, df):
    # TODO: implement your backtest logic
    return {}


# Setup logger
logger = logging.getLogger("portfolio_optimizations")
logging.basicConfig(level=logging.INFO)

# Example: metrics to try
metrics_to_try = [
    (PortfolioMetric.TOTAL_RETURN, OptimizationDirection.MAXIMIZE),
    (PortfolioMetric.MAX_DRAWDOWN, OptimizationDirection.MINIMIZE),
    (PortfolioMetric.SHARPE_RATIO, OptimizationDirection.MAXIMIZE),
]

symbol = "AAPL"  # TODO: set your symbol
your_data = None  # TODO: load your DataFrame
n_trials = 50

results = []
for metric, direction in metrics_to_try:
    optimizer = PortfolioStrategyOptimizer(
        strategy_class=YourStrategyClass,
        backtest_fn=your_backtest_fn,
        logger=logger,
        metric_name=metric,
        direction=direction,
    )
    result = optimizer.optimize(symbol=symbol, df=your_data, n_trials=n_trials)
    results.append(
        {"metric": metric.name, "direction": direction.name, "result": result}
    )

# Save results to disk
output_path = Path("portfolio_optimization_results.json")
with output_path.open("w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {output_path.resolve()}")
