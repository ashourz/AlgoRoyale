import numpy as np
import pandas as pd
import pytest

from algo_royale.backtester.evaluator.backtest.signal_backtest_evaluator import (
    SignalBacktestEvaluator,
)
from algo_royale.logging.logger_factory import mockLogger


@pytest.fixture
def evaluator():
    return SignalBacktestEvaluator(logger=mockLogger())


def valid_signals_df():
    return pd.DataFrame(
        {
            "timestamp": ["2025-07-09", "2025-07-10", "2025-07-11"],
            "close_price": [100, 110, 120],
            "entry_signal": [1, 0, 0],
            "exit_signal": [0, 1, 0],
        }
    )


def test_evaluate_signals_valid(evaluator):
    df = valid_signals_df()
    result = evaluator._evaluate_signals(df)
    assert isinstance(result, dict)
    assert "total_return" in result


def test_evaluate_signals_invalid(evaluator):
    df = pd.DataFrame({"timestamp": ["2025-07-09"], "close_price": [100]})
    with pytest.raises(ValueError):
        evaluator._evaluate_signals(df)


def test_validate_dataframe_with_extreme_values(evaluator):
    data = pd.DataFrame(
        {
            "timestamp": ["2025-07-09", "2025-07-10"],
            "close_price": [1e7, -100],
            "entry_signal": [1, 0],
            "exit_signal": [0, 1],
        }
    )
    with pytest.raises(ValueError):
        evaluator._validate_dataframe(data)


def test_simulate_trades_with_invalid_prices(evaluator):
    data = pd.DataFrame(
        {
            "timestamp": ["2025-07-09", "2025-07-10"],
            "close_price": [np.nan, np.inf],
            "entry_signal": [1, 0],
            "exit_signal": [0, 1],
        }
    )
    trades = evaluator._simulate_trades(data)
    assert len(trades) == 0


def test_simulate_trades_with_extreme_values(evaluator):
    data = pd.DataFrame(
        {
            "timestamp": ["2025-07-09", "2025-07-10"],
            "close_price": [1e7, 1e7],
            "entry_signal": [1, 0],
            "exit_signal": [0, 1],
        }
    )
    trades = evaluator._simulate_trades(data)
    assert len(trades) == 0


def test_sharpe_ratio(evaluator):
    returns = np.array([0.1, 0.2, 0.15, 0.05])
    result = evaluator._sharpe_ratio(returns)
    assert isinstance(result, float)
    assert result > 0


def test_sharpe_ratio_zero_std(evaluator):
    returns = np.array([0.1, 0.1, 0.1])
    result = evaluator._sharpe_ratio(returns)
    assert result == 0.0


def test_max_drawdown(evaluator):
    cum_returns = [0.1, 0.2, 0.15, 0.25, 0.1]
    result = evaluator._max_drawdown(cum_returns)
    assert isinstance(result, float)
    assert result >= 0
