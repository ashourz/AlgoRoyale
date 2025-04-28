from decimal import Decimal
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
            MovingAverageData(date=self.dates[i], close=Decimal(str(round(self.price_data[i], 2))))
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
        # Use more data points to ensure the crossover occurs
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('102')),
            MovingAverageData(date='2020-01-03', close=Decimal('104')),
            MovingAverageData(date='2020-01-04', close=Decimal('106')),
            MovingAverageData(date='2020-01-05', close=Decimal('108')),
            MovingAverageData(date='2020-01-06', close=Decimal('110')),
            MovingAverageData(date='2020-01-07', close=Decimal('115')),
            MovingAverageData(date='2020-01-08', close=Decimal('120')),
            MovingAverageData(date='2020-01-09', close=Decimal('125')),
        ]  # Simulate more increasing prices
    
        # Initialize strategy with short and long windows
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.historical_data)
    
        # Now the first crossover should occur at index 4 (after enough data points)
        self.assertEqual(signals[4], 'buy')  # The buy signal should appear at index 4

    def test_sell_signal(self):
        # Test case with synthetic data where a sell signal is expected
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('110')),
            MovingAverageData(date='2020-01-03', close=Decimal('105')),
            MovingAverageData(date='2020-01-04', close=Decimal('98')),
            MovingAverageData(date='2020-01-05', close=Decimal('90')),
        ]  # Simulate price changes
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.historical_data)

        # The first signal should be 'hold', but after the short MA crosses below the long MA, it should be 'sell'
        self.assertEqual(signals[1], 'hold')
        self.assertEqual(signals[2], 'sell')

    def test_edge_case(self):
        # Test case for edge case: Price stays flat, no signals should be generated
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('100')),
            MovingAverageData(date='2020-01-03', close=Decimal('100')),
            MovingAverageData(date='2020-01-04', close=Decimal('100')),
            MovingAverageData(date='2020-01-05', close=Decimal('100')),
            MovingAverageData(date='2020-01-06', close=Decimal('100')),
            MovingAverageData(date='2020-01-07', close=Decimal('100')),
            MovingAverageData(date='2020-01-08', close=Decimal('100')),
            MovingAverageData(date='2020-01-09', close=Decimal('100')),
            MovingAverageData(date='2020-01-10', close=Decimal('100')),
        ]  # Flat price data
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.historical_data)

        # If price stays flat, there should be no buy/sell signals
        self.assertTrue(all(signal == 'hold' for signal in signals))

    def test_no_data(self):
        # Test case for when no historical data is provided
        self.historical_data = []
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        try:
            signals = strategy.generate_signals(self.historical_data)
            self.fail
        except ValueError:
            pass


    def test_insufficient_data(self):
        # Test case for when there is insufficient data to calculate moving averages
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('102')),
        ]  # Less data than the long_window
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.historical_data)

        # If there is insufficient data, all signals should be 'hold'
        self.assertTrue(all(signal == 'hold' for signal in signals))

    def test_exact_window_data(self):
        # Test case for when the data length matches the long_window
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('102')),
            MovingAverageData(date='2020-01-03', close=Decimal('104')),
            MovingAverageData(date='2020-01-04', close=Decimal('106')),
            MovingAverageData(date='2020-01-05', close=Decimal('108')),
        ]  # Exactly 5 data points for long_window
        strategy = MovingAverageStrategy(short_window=3, long_window=5)
        signals = strategy.generate_signals(self.historical_data)

        # The first few signals should be 'hold' since moving averages cannot be calculated
        self.assertEqual(signals[0], 'hold')
        self.assertEqual(signals[-1], 'hold')  # No crossover in this data

    def test_fluctuating_prices(self):
        # Test case for fluctuating prices that cause multiple crossovers
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('100')),
            MovingAverageData(date='2020-01-02', close=Decimal('105')),
            MovingAverageData(date='2020-01-03', close=Decimal('102')),
            MovingAverageData(date='2020-01-04', close=Decimal('108')),
            MovingAverageData(date='2020-01-05', close=Decimal('103')),
            MovingAverageData(date='2020-01-06', close=Decimal('110')),
            MovingAverageData(date='2020-01-07', close=Decimal('107')),
        ]  # Fluctuating prices
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.historical_data)

        # Check for expected buy/sell signals based on crossovers
        self.assertEqual(signals[3], 'buy')  # Buy signal at index 2
        self.assertEqual(signals[4], 'sell')  # Sell signal at index 4
        self.assertEqual(signals[5], 'buy')  # Buy signal at index 5

    def test_decreasing_prices(self):
        # Test case for consistently decreasing prices
        self.historical_data = [
            MovingAverageData(date='2020-01-01', close=Decimal('120')),
            MovingAverageData(date='2020-01-02', close=Decimal('115')),
            MovingAverageData(date='2020-01-03', close=Decimal('110')),
            MovingAverageData(date='2020-01-04', close=Decimal('105')),
            MovingAverageData(date='2020-01-05', close=Decimal('100')),
        ]  # Decreasing prices
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.historical_data)

        # Check for expected sell signals
        self.assertEqual(signals[1], 'hold')  # Sell signal at index 2
        self.assertEqual(signals[2], 'sell')  # Hold signal at index 3
        