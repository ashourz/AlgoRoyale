import numpy as np
import pandas as pd
import pytest

from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.logging.logger_factory import mockLogger


@pytest.fixture
def evaluator():
    return PortfolioBacktestEvaluator(logger=mockLogger())


def valid_portfolio_df():
    return pd.DataFrame(
        {
            "portfolio_values": [100, 110, 120, 130],
            "portfolio_returns": [0.0, 0.1, 0.09, 0.083],
        }
    )


def test_evaluate_signals_valid(evaluator):
    df = valid_portfolio_df()
    result = evaluator._evaluate_signals(df)
    assert isinstance(result, dict)
    assert "total_return" in result
    assert result["total_return"] > 0


def test_evaluate_signals_empty(evaluator):
    df = pd.DataFrame({"portfolio_values": [], "portfolio_returns": []})
    result = evaluator._evaluate_signals(df)
    assert all(np.isnan(v) for v in result.values())


def test_evaluate_signals_invalid(evaluator):
    df = pd.DataFrame(
        {"portfolio_values": [100, None, 120], "portfolio_returns": [0.1, 0.2, None]}
    )
    with pytest.raises(ValueError):
        evaluator._evaluate_signals(df)


def test_evaluate_signals_zero_returns(evaluator):
    df = pd.DataFrame(
        {"portfolio_values": [100, 100, 100], "portfolio_returns": [0, 0, 0]}
    )
    result = evaluator._evaluate_signals(df)
    assert all(np.isnan(v) for v in result.values())


def test_evaluate_from_dict_valid(evaluator):
    result_dict = {
        "portfolio_values": [100, 110, 120],
        "metrics": {"portfolio_returns": [0.0, 0.1, 0.09]},
        "transactions": [1, 2, 3],
    }
    result = evaluator.evaluate_from_dict(result_dict)
    assert isinstance(result, dict)
    assert "total_return" in result


def test_evaluate_from_dict_length_mismatch(evaluator):
    result_dict = {
        "portfolio_values": [100, 110],
        "metrics": {"portfolio_returns": [0.0, 0.1, 0.09]},
    }
    with pytest.raises(ValueError):
        evaluator.evaluate_from_dict(result_dict)


def test_validate_dataframe_valid(evaluator):
    df = valid_portfolio_df()
    evaluator._validate_dataframe(df)  # Should not raise


def test_validate_dataframe_missing_column(evaluator):
    df = pd.DataFrame({"portfolio_values": [100, 110, 120]})
    with pytest.raises(ValueError):
        evaluator._validate_dataframe(df)


def test_validate_dataframe_nulls(evaluator):
    df = pd.DataFrame(
        {"portfolio_values": [100, None, 120], "portfolio_returns": [0.1, 0.2, 0.3]}
    )
    with pytest.raises(ValueError):
        evaluator._validate_dataframe(df)
    df2 = pd.DataFrame(
        {"portfolio_values": [100, 110, 120], "portfolio_returns": [0.1, None, 0.3]}
    )
    with pytest.raises(ValueError):
        evaluator._validate_dataframe(df2)


def test_max_drawdown_and_ratios(evaluator):
    returns = pd.Series([0.1, 0.2, -0.05, 0.15, -0.1])
    dd = evaluator.max_drawdown(returns)
    sortino = evaluator.sortino_ratio(returns)
    pf = evaluator.profit_factor(returns)
    assert isinstance(dd, float)
    assert isinstance(sortino, float)
    assert isinstance(pf, float)
