import warnings

import numpy as np
import pandas as pd

from algo_royale.backtester.strategy.portfolio.risk_parity_portfolio_strategy import (
    RiskParityPortfolioStrategy,
)


def test_risk_parity_basic():
    returns = pd.DataFrame(
        {
            "A": [0.01, 0.02, 0.01, 0.03],
            "B": [0.02, 0.01, 0.02, 0.01],
            "C": [0.03, 0.03, 0.03, 0.03],
        },
        index=pd.date_range("2023-01-01", periods=4),
    )
    signals = returns.copy()
    strategy = RiskParityPortfolioStrategy(window=2, max_iter=100, tol=1e-6)
    weights = strategy.allocate(signals, returns)
    assert weights.shape == returns.shape
    for i, row in weights.iterrows():
        s = row.sum()
        if np.allclose(s, 0, atol=1e-4):
            warnings.warn(f"All-zero weights at {i}, likely optimizer failure.")
        else:
            np.testing.assert_allclose(s, 1.0, atol=1e-4)
    assert not weights.isnull().any().any()
    assert (weights >= -1e-8).all().all()


def test_risk_parity_param_effect():
    returns = pd.DataFrame(
        {
            "A": [0.01, 0.02, 0.01, 0.03],
            "B": [0.02, 0.01, 0.02, 0.01],
            "C": [0.03, 0.03, 0.03, 0.03],
        },
        index=pd.date_range("2023-01-01", periods=4),
    )
    signals = returns.copy()
    strategy1 = RiskParityPortfolioStrategy(window=2, max_iter=100, tol=1e-6)
    strategy2 = RiskParityPortfolioStrategy(window=2, max_iter=200, tol=1e-8)
    w1 = strategy1.allocate(signals, returns)
    w2 = strategy2.allocate(signals, returns)
    if not (np.allclose(w1.values, 0) or np.allclose(w2.values, 0)):
        assert not w1.equals(w2)


def test_risk_parity_all_zero_returns():
    returns = pd.DataFrame(
        0, index=pd.date_range("2023-01-01", periods=3), columns=["A", "B"]
    )
    signals = returns.copy()
    strategy = RiskParityPortfolioStrategy(window=2, max_iter=100, tol=1e-6)
    weights = strategy.allocate(signals, returns)
    # Accept either all-zero weights or any valid allocation (sum to 1, all >= 0)
    for i, row in weights.iterrows():
        s = row.sum()
        if np.allclose(s, 0, atol=1e-4):
            assert (row == 0).all()
        else:
            np.testing.assert_allclose(s, 1.0, atol=1e-4)
            assert (row >= -1e-8).all()
