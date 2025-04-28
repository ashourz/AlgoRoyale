from unittest import TestCase
import numpy as np
import pandas as pd
from strategies.models.moving_average_data import MovingAverageData
from strategies.moving_average_strategy import MovingAverageStrategy

class TestMovingAverageStrategy(TestCase):
    def setUp(self):
        # Set up synthetic price data for testing
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2020-01-10', freq='B')  # 10 business days
        self.price_data = np.random.randn(len(self.dates)) * 5 + 100  # Simulated random close prices centered around 100
        
        # Create MovingAverageData objects for the historical data
        self.historical_data = [
            MovingAverageData(date=self.dates[i], close=round(self.price_data[i], 2))
            for i in range(len(self.dates))
        ]

    def test_generate_signals(self):
        strategy = MovingAverageStrategy(short_window=3, long_window=5)  # Using small windows for quick tests
        signals = strategy.generate_signals(self.historical_data)

        # Assert that the generated signals list is the same length as the historical data (minus one for the first day)
        self.assertEqual(len(signals), len(self.historical_data) - 1)

        # Example assertion: Check if the first signal is 'hold' (this will depend on the data and moving averages)
        self.assertEqual(signals[0], 'hold')

    def test_buy_signal(self):
        # Test case with specific synthetic data where a buy signal is expected
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=100),
            MovingAverageData(date='2020-01-02', close=102),
            MovingAverageData(date='2020-01-03', close=105),
            MovingAverageData(date='2020-01-04', close=107),
            MovingAverageData(date='2020-01-05', close=110),
        ]  # Simulate increasing prices
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.historical_data)

        # The first signal should be 'hold', but after the short MA crosses above the long MA, it should be 'buy'
        self.assertEqual(signals[1], 'buy')

    def test_sell_signal(self):
        # Test case with synthetic data where a sell signal is expected
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=100),
            MovingAverageData(date='2020-01-02', close=110),
            MovingAverageData(date='2020-01-03', close=105),
            MovingAverageData(date='2020-01-04', close=98),
            MovingAverageData(date='2020-01-05', close=90),
        ]  # Simulate price changes
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.historical_data)

        # The first signal should be 'hold', but after the short MA crosses below the long MA, it should be 'sell'
        self.assertEqual(signals[1], 'hold')
        self.assertEqual(signals[2], 'sell')

    def test_edge_case(self):
        # Test case for edge case: Price stays flat, no signals should be generated
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=100),
            MovingAverageData(date='2020-01-02', close=100),
            MovingAverageData(date='2020-01-03', close=100),
            MovingAverageData(date='2020-01-04', close=100),
            MovingAverageData(date='2020-01-05', close=100),
            MovingAverageData(date='2020-01-06', close=100),
            MovingAverageData(date='2020-01-07', close=100),
            MovingAverageData(date='2020-01-08', close=100),
            MovingAverageData(date='2020-01-09', close=100),
            MovingAverageData(date='2020-01-10', close=100),
        ]  # Flat price data
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.historical_data)

        # If price stays flat, there should be no buy/sell signals
        self.assertTrue(all(signal == 'hold' for signal in signals))
