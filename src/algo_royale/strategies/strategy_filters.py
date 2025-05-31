import pandas as pd


class StrategyFilter:
    """
    Base class for all strategy filters.
    """

    def __init__(self, *args, **kwargs):
        pass

    def apply(self, df: pd.DataFrame) -> pd.Series:
        """
        Should return a boolean Series where True means the filter passes.
        """
        raise NotImplementedError("Filter must implement apply(df)")


@staticmethod
def price_crosses_above_sma(current_row, prev_row, sma_col, close_col):
    """
    Returns True if the price crosses above the SMA between the previous and current rows.
    This indicates a potential shift into an uptrend.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        sma_col (str): Column name for the SMA values.
        close_col (str): Column name for the close price.

    Returns:
        bool: True if price crosses above SMA, else False.
    """
    return (
        prev_row[close_col] <= prev_row[sma_col]
        and current_row[close_col] > current_row[sma_col]
    )


@staticmethod
def price_crosses_below_sma(current_row, prev_row, sma_col, close_col):
    """
    Returns True if the price crosses below the SMA between the previous and current rows.
    This indicates a potential shift into a downtrend.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        sma_col (str): Column name for the SMA values.
        close_col (str): Column name for the close price.

    Returns:
        bool: True if price crosses below SMA, else False.
    """
    return (
        prev_row[close_col] >= prev_row[sma_col]
        and current_row[close_col] < current_row[sma_col]
    )


@staticmethod
def macd_bearish_cross(current_row, prev_row, macd_col, signal_col):
    """
    Returns True if MACD crosses below its signal line between previous and current rows,
    indicating bearish momentum.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        macd_col (str): Column name for the MACD values.
        signal_col (str): Column name for the MACD signal line values.

    Returns:
        bool: True if MACD crosses below signal line, else False.
    """
    return (
        prev_row[macd_col] >= prev_row[signal_col]
        and current_row[macd_col] < current_row[signal_col]
    )


@staticmethod
def adx_below_threshold(row, adx_col, threshold=25):
    """
    Returns True if the ADX value is below a specified threshold,
    indicating a weak or no trend environment.

    Args:
        row (pd.Series): A row of data.
        adx_col (str): Column name for the ADX values.
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX is below threshold, else False.
    """
    return row[adx_col] < threshold


@staticmethod
def volume_surge(row, volume_col, vol_ma_col, threshold=2.0):
    """
    Returns True if the current volume is greater than a multiple of its moving average,
    indicating a volume surge.

    Args:
        row (pd.Series): A row of data.
        volume_col (str): Column name for volume.
        vol_ma_col (str): Column name for volume moving average.
        threshold (float, optional): Multiplier threshold. Default is 2.0.

    Returns:
        bool: True if volume surges above threshold * moving average, else False.
    """
    return row[volume_col] > threshold * row[vol_ma_col]


@staticmethod
def volatility_spike(row, range_col, volatility_col):
    """
    Returns True if the current price range is greater than the volatility measure,
    indicating a volatility spike.

    Args:
        row (pd.Series): A row of data.
        range_col (str): Column name for the price range.
        volatility_col (str): Column name for the volatility value.

    Returns:
        bool: True if range is greater than volatility, else False.
    """
    return row[range_col] > row[volatility_col]


@staticmethod
def rsi_above_threshold(row, rsi_col, threshold=70):
    """
    Returns True if the RSI value is above a specified threshold,
    indicating overbought conditions.

    Args:
        row (pd.Series): A row of data.
        rsi_col (str): Column name for RSI values.
        threshold (float, optional): Threshold value. Default is 70.

    Returns:
        bool: True if RSI is above threshold, else False.
    """
    return row[rsi_col] > threshold


@staticmethod
def price_above_sma(row, sma_col, close_col):
    """
    Returns True if the price is above the SMA (indicating uptrend),
    else False.

    Args:
        row (pd.Series): A row of data.
        sma_col (str): Column name for SMA.
        close_col (str): Column name for close price.

    Returns:
        bool: True if price > SMA, else False.
    """
    return row[close_col] > row[sma_col]


class PriceAboveSMAFilter(StrategyFilter):
    def __init__(self, close_col: str, sma_col: str):
        self.close_col = close_col
        self.sma_col = sma_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.close_col] > df[self.sma_col]


@staticmethod
def price_below_sma(row, sma_col, close_col):
    """
    Returns True if the price is below the SMA (indicating downtrend),
    else False.

    Args:
        row (pd.Series): A row of data.
        sma_col (str): Column name for SMA.
        close_col (str): Column name for close price.

    Returns:
        bool: True if price < SMA, else False.
    """
    return row[close_col] < row[sma_col]


@staticmethod
def adx_above_threshold(row, adx_col, close_col, threshold=25):
    """
    Returns True if the ADX value is above a threshold (indicating strong trend).

    Args:
        row (pd.Series): A row of data.
        adx_col (str): Column name for ADX.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX > threshold, else False.
    """
    return row[adx_col] > threshold


@staticmethod
def rsi_below_threshold(row, rsi_col, close_col, threshold=30):
    """
    Returns True if the RSI value is below a threshold (indicating oversold).
    Can be used as a contrarian filter.

    Args:
        row (pd.Series): A row of data.
        rsi_col (str): Column name for RSI.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 30.

    Returns:
        bool: True if RSI < threshold, else False.
    """
    return row[rsi_col] < threshold


@staticmethod
def macd_bullish_cross(row, macd_col, signal_col, close_col):
    """
    Returns True if MACD is above its signal line (bullish momentum).
    Assumes you have columns 'macd' and 'macd_signal' in your DataFrame.

    Args:
        row (pd.Series): A row of data.
        macd_col (str): Column name for MACD.
        signal_col (str): Column name for MACD signal line.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).

    Returns:
        bool: True if MACD > signal line, else False.
    """
    return row[macd_col] > row[signal_col]
