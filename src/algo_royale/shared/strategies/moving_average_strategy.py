import pandas as pd
from typing import List

from shared.strategies.base_strategy import Strategy
from shared.strategies.models.moving_average_data import MovingAverageData

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType



logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION).get_logger()

class MovingAverageStrategy(Strategy):
    """
    A simple Moving Average Strategy for trading.
    The strategy generates trading signals based on two moving averages:
    - Buy when the short-term moving average crosses above the long-term moving average (Golden Cross).
    - Sell when the short-term moving average crosses below the long-term moving average (Death Cross).
    - Hold when no crossover occurs.
    
    Parameters:
    - short_window: The period for the short-term moving average (default: 50 days).
    - long_window: The period for the long-term moving average (default: 200 days).
    """

    def __init__(self, short_window=50, long_window=200):
        """
        Initialize the Moving Average Strategy.
        
        :param short_window: Short-term moving average window in days (default: 50 days)
            - Defines the period for the short-term moving average.
            - Typically, a shorter window (e.g., 10 or 20 days) reacts more quickly to price changes.
            - Suitable for identifying short-term trends or changes in momentum.
        
        :param long_window: Long-term moving average window in days (default: 200 days)
            - Defines the period for the long-term moving average.
            - Typically, a longer window (e.g., 50 or 200 days) smooths out price data and is slower to react.
            - Suitable for identifying the broader, long-term trend.
        """
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, historical_data: List[MovingAverageData]) -> List[str]:
        """
        Generate trading signals based on the moving average crossovers:
        - 'buy' if short-term moving average crosses above long-term moving average.
        - 'sell' if short-term moving average crosses below long-term moving average.
        - 'hold' otherwise.

        :param historical_data: List of MovingAverageData objects containing historical price data with a 'close' attribute.
        :return: A list of trading signals: 'buy', 'sell', 'hold'.
        """
        # Convert historical data to DataFrame
        df = MovingAverageData.to_dataframe(historical_data)

        # Ensure that 'df' contains 'close' prices
        if 'close' not in df.columns:
            raise ValueError("Historical data must contain 'close' price column.")
        
        # Log the raw close prices for debugging
        logger.debug(f"Raw Close Prices: {df['close'].tolist()}")

        # Calculate the moving averages
        df['short_ma'] = df['close'].rolling(window=self.short_window).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_window).mean()
        
        # Print calculated moving averages for debugging
        logger.debug(f"Short MA:{df['short_ma'].tolist()}")
        logger.debug(f"Long MA:{df['long_ma'].tolist()}")

        # Initialize signals with 'hold' for the first few periods before both MAs are calculable
        signals = ['hold'] * (max(self.short_window, self.long_window) - 1)

        # Generate signals starting from the day after both MAs are available
        for i in range(max(self.short_window, self.long_window), len(df)):
            logger.debug(f"Short MA at index {i}: {df['short_ma'].iloc[i]}")
            logger.debug(f"Long MA at index {i}: {df['long_ma'].iloc[i]}")
            
            # Ensure both MAs are calculated before making decisions
            if pd.isna(df['short_ma'].iloc[i]) or pd.isna(df['long_ma'].iloc[i]):
                signals.append('hold')
                continue
            
            # Buy when short MA crosses above long MA (Golden Cross)
            if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] <= df['long_ma'].iloc[i-1]:
                signals.append('buy')
            # Sell when short MA crosses below long MA (Death Cross)
            elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] >= df['long_ma'].iloc[i-1]:
                signals.append('sell')
            # Adjust this to allow for smoother transitions
            elif df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] > df['long_ma'].iloc[i-1]:
                signals.append('buy')  # Smooth transition to buy if the short MA is still above the long MA
            elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] < df['long_ma'].iloc[i-1]:
                signals.append('sell')  # Smooth transition to sell if the short MA is still below the long MA
            else:
                signals.append('hold')  # Hold when there's no crossover

        # Print final signals for debugging
        logger.debug(f"Signals:{signals}")
        return signals