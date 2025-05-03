from unittest import TestCase
from decimal import Decimal
import numpy as np
import pandas as pd
from algo_royale.shared.strategies.moving_average_strategy import MovingAverageStrategy

class TestMovingAverageStrategy(TestCase):

    def setUp(self):
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2020-01-10', freq='B')  # 10 business days
        self.price_data = np.random.randn(len(self.dates)) * 5 + 100  # Simulated close prices
        self.df = pd.DataFrame({
            'date': self.dates,
            'close': self.price_data.round(2)
        })

    def test_generate_signals(self):
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.df)
        self.assertEqual(len(signals), len(self.df))
        self.assertEqual(signals[0], 'hold')

    def test_buy_signal(self):
        prices = [100, 102, 104, 106, 108, 110, 115, 120, 125]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=len(prices), freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(df)
        self.assertEqual(signals[5], 'buy')

    def test_sell_signal(self):
        prices = [100, 110, 105, 98, 90]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=len(prices), freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(df)
        self.assertEqual(signals[2], 'hold')
        self.assertEqual(signals[3], 'sell')

    def test_edge_case_flat_prices(self):
        prices = [100] * 10
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=10, freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(df)
        self.assertTrue(all(signal == 'hold' for signal in signals))

    def test_no_data(self):
        df = pd.DataFrame(columns=['date', 'close'])
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(df)
        self.assertTrue(all(signal == 'hold' for signal in signals))


    def test_insufficient_data(self):
        prices = [100, 102]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=2, freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(df)
        self.assertTrue(all(signal == 'hold' for signal in signals))

    def test_exact_window_data(self):
        prices = [100, 102, 104, 106, 108]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5, freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(df)
        self.assertEqual(signals[0], 'hold')
        self.assertEqual(signals[-1], 'hold')

    def test_fluctuating_prices(self):
        prices = [100, 105, 102, 108, 103, 110, 107]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=7, freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(df)
        self.assertEqual(signals[4], 'buy')
        self.assertEqual(signals[5], 'sell')
        self.assertEqual(signals[6], 'buy')

    def test_decreasing_prices(self):
        prices = [120, 115, 110, 105, 100]
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5, freq='D'),
            'close': prices
        })
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(df)
        self.assertEqual(signals[2], 'hold')
        self.assertEqual(signals[3], 'sell')
