from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)


class DummyStrategy:
    def allocate(self, data, _):
        # Allocate 100% to first asset, 0% to others
        weights = np.zeros_like(data.values)
        weights[:, 0] = 1.0
        return pd.DataFrame(weights, columns=data.columns, index=data.index)


def make_test_data():
    # 3 time steps, 2 assets
    return pd.DataFrame(
        {
            "A": [10, 11, 12],
            "B": [20, 19, 18],
        },
        index=pd.date_range("2022-01-01", periods=3),
    )


@pytest.mark.parametrize(
    "initial_balance,transaction_cost,min_lot,leverage,slippage",
    [
        (1000, 0.0, 1, 1.0, 0.0),
        (1000, 0.01, 1, 1.0, 0.0),
        (1000, 0.0, 10, 1.0, 0.0),
        (1000, 0.0, 1, 2.0, 0.0),
        (1000, 0.0, 1, 1.0, 0.01),
    ],
)
def test_portfolio_backtest_executor_basic(
    initial_balance, transaction_cost, min_lot, leverage, slippage
):
    executor = PortfolioBacktestExecutor(
        logger=MagicMock(),
        initial_balance=initial_balance,
        transaction_cost=transaction_cost,
        min_lot=min_lot,
        leverage=leverage,
        slippage=slippage,
    )
    data = make_test_data()
    strat = DummyStrategy()
    results = executor.run_backtest(strat, data)
    assert "portfolio_values" in results
    assert "cash_history" in results
    assert "holdings_history" in results
    assert "transactions" in results
    assert isinstance(results["portfolio_values"], list)
    assert isinstance(results["cash_history"], list)
    assert isinstance(results["holdings_history"], list)
    assert isinstance(results["transactions"], list)
    assert len(results["portfolio_values"]) == len(data)
    assert len(results["cash_history"]) == len(data)
    assert len(results["holdings_history"]) == len(data)
    # Final cash and holdings should be floats/arrays
    assert isinstance(results["final_cash"], (int, float))
    assert isinstance(results["final_holdings"], np.ndarray)


def test_portfolio_backtest_executor_trades():
    executor = PortfolioBacktestExecutor(logger=MagicMock(), initial_balance=1000)
    data = make_test_data()
    strat = DummyStrategy()
    results = executor.run_backtest(strat, data)
    # Should have at least one buy transaction
    buy_trades = [t for t in results["transactions"] if t["action"] == "buy"]
    assert len(buy_trades) > 0
    # No negative cash
    assert all(c >= 0 for c in results["cash_history"])
    # Holdings for asset A should increase
    holdings = np.array([h[0] for h in results["holdings_history"]])
    assert np.all(holdings[:-1] <= holdings[1:])
