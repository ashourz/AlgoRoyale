import pandas as pd
import pytest

from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer import (
    MockPortfolioStrategyOptimizer,
    PortfolioStrategyOptimizerImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer import (
    MockSignalStrategyOptimizer,
    SignalStrategyOptimizerImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    MockSignalStrategyOptimizerFactory,
    SignalStrategyOptimizerFactoryImpl,
)
from tests.mocks.mock_loggable import MockLoggable


class DummyStrategy:
    @staticmethod
    def optuna_suggest(logger, trial):
        return {}

    def __init__(self, logger, **kwargs):
        self.logger = logger
        self.kwargs = kwargs


def dummy_backtest_fn(strategy, df):
    return {"metrics": {"total_return": 1.0, "sharpe_ratio": 2.0}}


def test_portfolio_strategy_optimizer_success():
    logger = MockLoggable()
    strategy_logger = MockLoggable()
    optimizer = PortfolioStrategyOptimizerImpl(
        strategy_class=DummyStrategy,
        backtest_fn=dummy_backtest_fn,
        logger=logger,
        strategy_logger=strategy_logger,
    )
    df = pd.DataFrame({"close_price": [1, 2, 3, 4, 5]})
    import asyncio

    result = asyncio.run(optimizer.optimize(["SYM1"], df, n_trials=2))
    assert result["strategy"] == "DummyStrategy"
    assert "metrics" in result
    assert result["metrics"]["total_return"] == 1.0


def test_portfolio_strategy_optimizer_error(monkeypatch):
    logger = MockLoggable()
    strategy_logger = MockLoggable()

    def bad_backtest_fn(strategy, df):
        raise RuntimeError("fail")

    optimizer = PortfolioStrategyOptimizerImpl(
        strategy_class=DummyStrategy,
        backtest_fn=bad_backtest_fn,
        logger=logger,
        strategy_logger=strategy_logger,
    )
    df = pd.DataFrame({"close_price": [1, 2, 3, 4, 5]})
    import asyncio

    result = asyncio.run(optimizer.optimize(["SYM1"], df, n_trials=1))
    assert result["error"]


def test_mock_portfolio_strategy_optimizer():
    optimizer = MockPortfolioStrategyOptimizer()
    mock_result = {"foo": "bar"}
    optimizer.setOptimizeResults(mock_result)
    import asyncio

    result = asyncio.run(optimizer.optimize("SYM1", pd.DataFrame({}), 1))
    assert result == mock_result
    optimizer.resetOptimizeResults()
    with pytest.raises(ValueError):
        asyncio.run(optimizer.optimize("SYM1", pd.DataFrame({}), 1))


def test_signal_strategy_optimizer_factory_create():
    logger = MockLoggable()
    strategy_logger = MockLoggable()
    factory = SignalStrategyOptimizerFactoryImpl(logger, strategy_logger)
    optimizer = factory.create(DummyStrategy, {}, dummy_backtest_fn)
    assert isinstance(optimizer, SignalStrategyOptimizerImpl)


def test_mock_signal_strategy_optimizer_factory():
    factory = MockSignalStrategyOptimizerFactory()
    factory.setCreatedOptimizerResult({"foo": "bar"})
    optimizer = factory.create(DummyStrategy, {}, dummy_backtest_fn)
    assert isinstance(optimizer, MockSignalStrategyOptimizer)
    optimizer.setOptimizeResults({"foo": "bar"})
    result = optimizer.optimize("SYM1", pd.DataFrame({}), None, None, 1)
    assert result == {"foo": "bar"}
    factory.resetCreatedOptimizers()


def test_signal_strategy_optimizer_impl(monkeypatch):
    logger = MockLoggable()
    strategy_logger = MockLoggable()

    class DummyCond:
        @staticmethod
        def optuna_suggest(logger, trial, prefix=None):
            return {}

    async def async_backtest_fn(strategy, df):
        return {
            "total_return": 1.0,
            "sharpe_ratio": 2.0,
            "win_rate": 0.5,
            "max_drawdown": 0.1,
        }

    optimizer = SignalStrategyOptimizerImpl(
        strategy_class=DummyStrategy,
        condition_types={
            "entry": [DummyCond],
            "trend": [],
            "exit": [],
            "stateful_logic": [],
        },
        backtest_fn=async_backtest_fn,
        logger=logger,
        strategy_logger=strategy_logger,
    )
    df = pd.DataFrame({"close_price": [1, 2, 3, 4, 5]})
    result = optimizer.optimize("SYM1", df, None, None, n_trials=1)
    print("DEBUG: result=", result)
    assert result["strategy"] == "DummyStrategy"
    assert "metrics" in result
    assert result["metrics"]["total_return"] == 1.0

    # Error case
    async def bad_async_backtest_fn(strategy, df):
        raise RuntimeError("fail")

    optimizer = SignalStrategyOptimizerImpl(
        strategy_class=DummyStrategy,
        condition_types={
            "entry": [DummyCond],
            "trend": [],
            "exit": [],
            "stateful_logic": [],
        },
        backtest_fn=bad_async_backtest_fn,
        logger=logger,
        strategy_logger=strategy_logger,
    )
    with pytest.raises(RuntimeError):
        optimizer.optimize("SYM1", df, None, None, n_trials=1)
