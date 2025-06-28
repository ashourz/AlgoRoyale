from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer import (
    OptimizationDirection,
    PortfolioMetric,
    PortfolioStrategyOptimizer,
)


class DummyStrategy:
    __name__ = "DummyStrategy"

    def __init__(self, a=1):
        self.a = a

    @staticmethod
    def optuna_suggest(trial, prefix=""):
        return {"a": 1}


def dummy_backtest_fn(strategy, df):
    # Return all metrics for testing
    return {
        "metrics": {
            "total_return": 0.5,
            "max_drawdown": 0.1,
            "sharpe_ratio": 2.0,
        }
    }


def make_df():
    return pd.DataFrame({"A": [1, 2, 3]})


@pytest.mark.asyncio
async def test_single_objective():
    logger = MagicMock()
    optimizer = PortfolioStrategyOptimizer(
        strategy_class=DummyStrategy,
        backtest_fn=dummy_backtest_fn,
        logger=logger,
        metric_name=PortfolioMetric.TOTAL_RETURN,
        direction=OptimizationDirection.MAXIMIZE,
    )
    result = await optimizer.optimize("AAPL", make_df(), n_trials=1)
    assert result["strategy"] == "DummyStrategy"
    assert result["meta"]["multi_objective"] is False
    assert result["best_value"] == 0.5
    metrics = result["metrics"]
    if isinstance(metrics, list):
        metrics = metrics[0]
    assert metrics["total_return"] == 0.5


@pytest.mark.asyncio
async def test_multi_objective():
    logger = MagicMock()
    optimizer = PortfolioStrategyOptimizer(
        strategy_class=DummyStrategy,
        backtest_fn=dummy_backtest_fn,
        logger=logger,
        metric_name=[PortfolioMetric.TOTAL_RETURN, PortfolioMetric.SHARPE_RATIO],
        direction=[OptimizationDirection.MAXIMIZE, OptimizationDirection.MAXIMIZE],
    )
    result = await optimizer.optimize("AAPL", make_df(), n_trials=1)
    assert result["meta"]["multi_objective"] is True
    assert isinstance(result["best_value"], list)
    assert len(result["best_value"]) == 1
    # metrics is a list of dicts, check the first one
    assert result["metrics"][0]["total_return"] == 0.5
    assert result["metrics"][0]["sharpe_ratio"] == 2.0


@pytest.mark.asyncio
async def test_metric_extraction_failure():
    logger = MagicMock()

    def bad_backtest_fn(strategy, df):
        return {}

    optimizer = PortfolioStrategyOptimizer(
        strategy_class=DummyStrategy,
        backtest_fn=bad_backtest_fn,
        logger=logger,
        metric_name=PortfolioMetric.TOTAL_RETURN,
        direction=OptimizationDirection.MAXIMIZE,
    )
    result = await optimizer.optimize("AAPL", make_df(), n_trials=1)
    assert result["best_value"] == float("-inf")
