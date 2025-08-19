from enum import Enum


class SymbolHoldStatus(Enum):
    HOLD_ALL = "hold_all"
    BUY_ONLY = "buy_only"
    SELL_ONLY = "sell_only"
    CLOSED = "closed"
