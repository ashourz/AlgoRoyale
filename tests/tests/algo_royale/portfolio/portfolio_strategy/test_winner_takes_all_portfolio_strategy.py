import warnings

import numpy as np
import pandas as pd

from algo_royale.backtester.strategy.portfolio.winner_takes_all_portfolio_strategy import (
    WinnerTakesAllPortfolioStrategy,
)


def test_winner_takes_all_basic():
    returns = pd.DataFrame(
        {
            "A": [0.01, 0.02, 0.01, 0.03],
            "B": [0.02, 0.01, 0.02, 0.01],
            "C": [0.03, 0.03, 0.03, 0.03],
        },
        index=pd.date_range("2023-01-01", periods=4),
    )
    signals = returns.copy()
    strategy = WinnerTakesAllPortfolioStrategy(
        use_signals=True, move_to_cash_at_end_of_day=False
    )
    weights = strategy._allocate(signals, returns)
    assert weights.shape == returns.shape
    for i, row in weights.iterrows():
        s = row.sum()
        if np.allclose(s, 0, atol=1e-4):
            warnings.warn(f"All-zero weights at {i}, likely no positive signal/return.")
        else:
            np.testing.assert_allclose(s, 1.0, atol=1e-4)
        # Each row should have at most one 1.0 and the rest 0.0
        assert (row == 1.0).sum() <= 1
        assert ((row == 0.0) | (row == 1.0)).all()
    assert not weights.isnull().any().any()


def test_winner_takes_all_move_to_cash():
    returns = pd.DataFrame(
        {
            "A": [0.01, 0.02, 0.01, 0.03],
            "B": [0.02, 0.01, 0.02, 0.01],
            "C": [0.03, 0.03, 0.03, 0.03],
        },
        index=pd.date_range("2023-01-01", periods=4),
    )
    signals = returns.copy()
    strategy = WinnerTakesAllPortfolioStrategy(
        use_signals=True, move_to_cash_at_end_of_day=True
    )
    weights = strategy._allocate(signals, returns)
    assert (weights.iloc[-1] == 0.0).all()


def test_winner_takes_all_all_zero_returns():
    returns = pd.DataFrame(
        0, index=pd.date_range("2023-01-01", periods=3), columns=["A", "B"]
    )
    signals = returns.copy()
    strategy = WinnerTakesAllPortfolioStrategy(
        use_signals=True, move_to_cash_at_end_of_day=False
    )
    weights = strategy._allocate(signals, returns)
    assert (weights == 0).all().all()
