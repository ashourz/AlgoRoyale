import logging
from typing import List
import pandas as pd
import numpy as np
from algo_royale.shared.strategies.base_strategy import Strategy
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION).get_logger()

class MovingAverageStrategy(Strategy):
    """
    Enhanced Moving Average Crossover Strategy with:
    - Vectorized signal calculation
    - Additional validation
    - Performance optimizations
    - Configurable signal values
    """
    
    def __init__(self, 
                 short_window: int = 50, 
                 long_window: int = 200,
                 close_col: str = 'close',
                 buy_signal: str = 'buy',
                 sell_signal: str = 'sell',
                 hold_signal: str = 'hold'):
        """
        Args:
            short_window: Short moving average window
            long_window: Long moving average window  
            close_col: Name of column containing close prices
            buy_signal: Value to use for buy signals
            sell_signal: Value to use for sell signals
            hold_signal: Value to use for hold signals
        """
        self.short_window = short_window
        self.long_window = long_window
        self.close_col = close_col
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal
        self.hold_signal = hold_signal
        
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
            
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Fixed signal generation without bitwise operations on floats"""
        # Validation
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
            
        if self.close_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {self.close_col}")
            
        if len(df) < max(self.short_window, self.long_window):
            logger.warning("Not enough data for full windows - returning all holds")
            return pd.Series(self.hold_signal, index=df.index, name='signal')
        
        # Calculate moving averages
        closes = df[self.close_col]
        df['short_ma'] = closes.rolling(window=self.short_window, min_periods=1).mean()
        df['long_ma'] = closes.rolling(window=self.long_window, min_periods=1).mean()
        
        # Initialize all signals as hold
        signals = pd.Series(self.hold_signal, index=df.index, name='signal')
        
        # Calculate conditions using comparison operators instead of bitwise
        short_above_long = df['short_ma'] > df['long_ma']
        prev_short_above_long = short_above_long.shift(1).fillna(False)
        
        # Golden Cross (buy) - when short MA crosses above long MA
        golden_cross = short_above_long & (~prev_short_above_long)
        signals[golden_cross] = self.buy_signal
        
        # Death Cross (sell) - when short MA crosses below long MA
        death_cross = (~short_above_long) & prev_short_above_long
        signals[death_cross] = self.sell_signal
        
        # Existing trends
        signals[short_above_long & (signals == self.hold_signal)] = self.buy_signal
        signals[(~short_above_long) & (signals == self.hold_signal)] = self.sell_signal
        
        return signals

    def get_required_columns(self) -> List[str]:
        """Return list of columns needed in input DataFrame"""
        return [self.close_col]

    def get_min_data_points(self) -> int:
        """Return minimum data points needed to generate signals"""
        return max(self.short_window, self.long_window)