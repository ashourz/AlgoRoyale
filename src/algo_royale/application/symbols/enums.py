from enum import Enum


## TODO: ENSURE ALL SYMBOL HOLD STATUS VALUES ARE HANDLED
class SymbolHoldStatus(Enum):
    START = "start"
    HOLD_ALL = "hold_all"
    BUY_ONLY = "buy_only"
    SELL_ONLY = "sell_only"
    POST_FILL_DELAY = "delay_until"
    PENDING_SETTLEMENT = "pending_settlement"
    CLOSED_FOR_DAY = "closed_for_day"
