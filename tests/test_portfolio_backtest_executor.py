import unittest
from unittest.mock import Mock

import numpy as np
import pandas as pd

from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.logging.logger_singleton import mockLogger


class TestPortfolioBacktestExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = PortfolioBacktestExecutor(
            logger=mockLogger(),
            initial_balance=1_000_000.0,
            transaction_cost=0.001,
            min_lot=1,
            leverage=1.0,
            slippage=0.0,
        )

        # Mock strategies
        self.mock_strategy_extreme_price = Mock()
        self.mock_strategy_extreme_price.allocate.return_value = pd.DataFrame(
            {
                "asset_1": [0.5, 0.5],
                "asset_2": [0.5, 0.5],
            }
        )

        self.mock_strategy_extreme_quantity = Mock()
        self.mock_strategy_extreme_quantity.allocate.return_value = pd.DataFrame(
            {
                "asset_1": [1e10, 1e10],
                "asset_2": [1e10, 1e10],
            }
        )

        self.mock_strategy_numerical_stability = Mock()
        self.mock_strategy_numerical_stability.allocate.return_value = pd.DataFrame(
            {
                "asset_1": [np.nan, np.nan],
                "asset_2": [np.inf, np.inf],
            }
        )

    def test_extreme_price_validation(self):
        data = pd.DataFrame(
            {
                "asset_1": [1e7, 1e7],
                "asset_2": [1e7, 1e7],
            }
        )
        results = self.executor.run_backtest(self.mock_strategy_extreme_price, data)
        self.assertEqual(
            len(results["transactions"]),
            0,
            "Transactions should be skipped due to extreme prices.",
        )

    def test_extreme_quantity_validation(self):
        data = pd.DataFrame(
            {
                "asset_1": [100, 100],
                "asset_2": [100, 100],
            }
        )
        results = self.executor.run_backtest(self.mock_strategy_extreme_quantity, data)
        self.assertEqual(
            len(results["transactions"]),
            0,
            "Transactions should be skipped due to extreme quantities.",
        )

    def test_numerical_stability(self):
        data = pd.DataFrame(
            {
                "asset_1": [100, 100],
                "asset_2": [100, 100],
            }
        )
        results = self.executor.run_backtest(
            self.mock_strategy_numerical_stability, data
        )
        self.assertEqual(
            len(results["transactions"]),
            0,
            "Transactions should be skipped due to numerical instability.",
        )

    def test_mixed_valid_invalid_data(self):
        data = pd.DataFrame(
            {
                "asset_1": [1e7, 100],
                "asset_2": [1e7, -100],
            }
        )
        results = self.executor.run_backtest(self.mock_strategy_extreme_price, data)
        self.assertEqual(
            len(results["transactions"]),
            0,
            "Transactions should be skipped due to mixed valid and invalid data.",
        )

    def test_logging_for_skipped_trades(self):
        with self.assertLogs(self.executor.logger, level="WARNING") as log:
            data = pd.DataFrame(
                {
                    "asset_1": [np.nan, 1e7],
                    "asset_2": [np.inf, 1e7],
                }
            )
            self.executor.run_backtest(self.mock_strategy_numerical_stability, data)
            self.assertTrue(
                any("Skipping" in message for message in log.output),
                "Warnings for skipped trades should be logged.",
            )

    def test_output_structure_validation(self):
        data = pd.DataFrame(
            {
                "asset_1": [100, 100],
                "asset_2": [100, 100],
            }
        )
        results = self.executor.run_backtest(self.mock_strategy_extreme_price, data)
        self.assertIn(
            "portfolio_values", results, "Output should contain portfolio_values."
        )
        self.assertIn("cash_history", results, "Output should contain cash_history.")
        self.assertIn(
            "holdings_history", results, "Output should contain holdings_history."
        )
        self.assertIn("transactions", results, "Output should contain transactions.")


if __name__ == "__main__":
    unittest.main()
