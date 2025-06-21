import numpy as np
import pandas as pd

from algo_royale.portfolio.portfolio_strategy.equal_weight_portfolio_strategy import (
    EqualWeightPortfolioStrategy,
)


def test_equal_weight_portfolio_strategy_basic():
    signals = pd.DataFrame(
        {"AAPL": [1, 0, 1], "GOOGL": [0, 1, 1], "MSFT": [1, 1, 0]},
        index=pd.date_range("2023-01-01", periods=3),
    )
    returns = pd.DataFrame(
        {
            "AAPL": [0.01, -0.02, 0.03],
            "GOOGL": [-0.01, 0.02, 0.01],
            "MSFT": [0.02, -0.01, 0.02],
        },
        index=pd.date_range("2023-01-01", periods=3),
    )
    strategy = EqualWeightPortfolioStrategy()
    weights = strategy.allocate(signals, returns)
    # Check shape
    assert weights.shape == signals.shape
    # Check weights sum to 1
    np.testing.assert_allclose(weights.sum(axis=1).values, 1.0)
    # Check no NaNs
    assert not weights.isnull().any().any()
    # Check all weights are equal
    expected = pd.DataFrame(1.0 / 3, index=signals.index, columns=signals.columns)
    pd.testing.assert_frame_equal(weights, expected)
