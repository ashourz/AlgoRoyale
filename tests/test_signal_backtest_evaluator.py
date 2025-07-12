import unittest

import numpy as np
import pandas as pd

from algo_royale.backtester.evaluator.backtest.signal_backtest_evaluator import (
    SignalBacktestEvaluator,
)
from algo_royale.logging.logger_factory import mockLogger


class TestSignalBacktestEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = SignalBacktestEvaluator(logger=mockLogger())

    def test_validate_dataframe_with_extreme_values(self):
        data = pd.DataFrame(
            {
                "timestamp": ["2025-07-09", "2025-07-10"],
                "close_price": [1e7, -100],
                "entry_signal": [1, 0],
                "exit_signal": [0, 1],
            }
        )
        with self.assertRaises(ValueError):
            self.evaluator._validate_dataframe(data)

    def test_simulate_trades_with_invalid_prices(self):
        data = pd.DataFrame(
            {
                "timestamp": ["2025-07-09", "2025-07-10"],
                "close_price": [np.nan, np.inf],
                "entry_signal": [1, 0],
                "exit_signal": [0, 1],
            }
        )
        trades = self.evaluator._simulate_trades(data)
        self.assertEqual(
            len(trades), 0, "Trades should be skipped due to invalid prices."
        )

    def test_simulate_trades_with_extreme_values(self):
        data = pd.DataFrame(
            {
                "timestamp": ["2025-07-09", "2025-07-10"],
                "close_price": [1e7, 1e7],
                "entry_signal": [1, 0],
                "exit_signal": [0, 1],
            }
        )
        trades = self.evaluator._simulate_trades(data)
        self.assertEqual(
            len(trades), 0, "Trades should be skipped due to extreme values."
        )


if __name__ == "__main__":
    unittest.main()
