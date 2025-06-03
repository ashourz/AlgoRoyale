from enum import Enum


class SignalType(Enum):
    """Enum representing the different types of trading signals.

    Attributes:
        BUY (str): Indicates a buy signal.
        SELL (str): Indicates a sell signal.
        HOLD (str): Indicates a hold signal.
        SHORT (str): Indicates a short signal.
        COVER (str): Indicates a cover signal.

    Usage:
        You can use these constants to represent trading signals in your strategy logic.
        signals = pd.Series(SignalType.HOLD.value, index=df.index, name="signal")
        ...
        signals.iloc[i] = SignalType.BUY.value
        ...
        signals.iloc[i] = SignalType.SELL.value
    """

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    SHORT = "short"
    COVER = "cover"
