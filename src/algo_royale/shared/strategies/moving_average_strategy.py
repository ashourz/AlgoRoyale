import pandas as pd
from typing import List
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION).get_logger()

class MovingAverageStrategy(Strategy):
    """
    Maintains the exact same signal generation logic as the original,
    but works directly with DataFrames instead of MovingAverageData objects.
    """
    
    def __init__(self, short_window: int = 50, long_window: int = 200, 
                 close_col: str = 'close'):
        self.short_window = short_window
        self.long_window = long_window
        self.close_col = close_col
        
    def generate_signals(self, df: pd.DataFrame) -> List[str]:
        """
        Generate signals with identical logic to original version.
        
        Args:
            df: DataFrame containing at least:
                - A column with close prices (default 'close')
                - Enough rows for the longest window
            
        Returns:
            List of signals: 'buy', 'sell', or 'hold'
        """
        # Validation
        if self.close_col not in df.columns:
            raise ValueError(f"DataFrame must contain '{self.close_col}' column")
            
        if len(df) < max(self.short_window, self.long_window):
            return ['hold'] * len(df)

        closes = df[self.close_col]
        
        # Calculate moving averages
        df['short_ma'] = closes.rolling(window=self.short_window).mean()
        df['long_ma'] = closes.rolling(window=self.long_window).mean()
        
        logger.debug(f"Close prices: {closes.tolist()}")
        logger.debug(f"Short MA: {df['short_ma'].tolist()}")
        logger.debug(f"Long MA: {df['long_ma'].tolist()}")
        
        # Initialize ALL signals with 'hold' first
        signals = ['hold'] * len(df)
        
        # Generate signals with original logic starting from valid point
        for i in range(max(self.short_window, self.long_window), len(df)):
            current_short = df['short_ma'].iloc[i]
            current_long = df['long_ma'].iloc[i]
            prev_short = df['short_ma'].iloc[i-1]
            prev_long = df['long_ma'].iloc[i-1]
            
            logger.debug(f"Index {i}: Short={current_short}, Long={current_long}")
            
            if pd.isna(current_short) or pd.isna(current_long):
                continue  # Keep as 'hold' since we pre-filled
            
            # 1. Golden Cross (buy signal)
            if current_short > current_long and prev_short <= prev_long:
                signals[i] = 'buy'
            
            # 2. Death Cross (sell signal)
            elif current_short < current_long and prev_short >= prev_long:
                signals[i] = 'sell'
            
            # 3. Smooth buy transition (already above)
            elif current_short > current_long and prev_short > prev_long:
                signals[i] = 'buy'
            
            # 4. Smooth sell transition (already below)
            elif current_short < current_long and prev_short < prev_long:
                signals[i] = 'sell'
            
            # 5. No crossover - remains 'hold'
        
        logger.debug(f"Final signals: {signals}")
        return signals