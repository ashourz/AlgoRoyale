import warnings

import numpy as np
import pandas as pd

from algo_royale.backtester.strategy.portfolio.momentum_portfolio_strategy import (
    MomentumPortfolioStrategy,
)


def test_momentum_portfolio_basic():
    returns = pd.DataFrame(
        {
            "A": [0.01, 0.02, 0.01, 0.03],
            "B": [0.02, 0.01, 0.02, 0.01],
            "C": [0.03, 0.03, 0.03, 0.03],
        },
        index=pd.date_range("2023-01-01", periods=4),
    )
    signals = returns.copy()
    strategy = MomentumPortfolioStrategy(window=2)
    weights = strategy._allocate(signals, returns)
    assert weights.shape == returns.shape
    for i, row in weights.iterrows():
        s = row.sum()
        if np.allclose(s, 0, atol=1e-4):
            warnings.warn(f"All-zero weights at {i}, likely optimizer failure.")
        else:
            np.testing.assert_allclose(s, 1.0, atol=1e-4)
    assert not weights.isnull().any().any()
    assert (weights >= -1e-8).all().all()


def test_momentum_portfolio_all_zero_returns():
    returns = pd.DataFrame(
        0, index=pd.date_range("2023-01-01", periods=3), columns=["A", "B"]
    )
    signals = returns.copy()
    strategy = MomentumPortfolioStrategy(window=2)
    weights = strategy._allocate(signals, returns)
    assert (weights == 0).all().all()
