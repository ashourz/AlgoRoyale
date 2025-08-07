from enum import Enum


class EquityOrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class EquityOrderType(str, Enum):
    """
    Type of order to place.

    The following provides a comprehensive breakdown of the supported order types for each category:

    - Equity trading: market, limit, stop, stop_limit, trailing_stop.
    - Options trading: market, limit, stop, stop_limit.
    - Multileg Options trading: market, limit.
    - Crypto trading: market, limit, stop_limit.
    """

    MARKET = "market"  # Executes immediately at market price
    LIMIT = "limit"  # Executes at a specific price or better
    STOP = "stop"  # Becomes a market order when stop_price is hit
    STOP_LIMIT = "stop_limit"  # Becomes a limit order when stop_price is hit
    TRAILING_STOP = "trailing_stop"  # Adjusts with market price offset


class EquityTimeInForce(str, Enum):
    """Time in force options for equity orders."""

    DAY = "day"  # Valid only for the trading day
    GTC = "gtc"  # Good-Til-Cancelled
    OPG = "opg"  # On the Open
    CLS = "cls"  # On the Close
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


class EquityOrderClass(str, Enum):
    """Order classes for equity trading."""

    SIMPLE = "simple"  # Single leg order
    OCO = "oco"  # One Cancels Other
    OTO = "oto"  # One Triggers Other
    BRACKET = "bracket"  # Bracket order
