

from enum import Enum

class IntradayReporting(str, Enum):
    """
    Type of intraday reporting for portfolio history.
    
    The following provides a comprehensive breakdown of the supported intraday reporting types:

    - MARKET_HOURS: Only timestamps for the core requity trading hours are returned (usually 9:30am to 4:00pm, trading days only)
    - EXTENDED_HOURS: Returns timestamps for the whole session including extended hours (usually 4:00am to 8:00pm, trading days only)
    - CONTINUOUS: Returns price data points 24/7 (for off-session times too). To calculate the equity values we are using the following prices:
        - Between 4:00am and 10:00pm on trading days the valuation will be calculated based on the last trade (extended hours and normal hours respectively).
        - After 10:00pm, until the next session open the equities will be valued at their official closing price on the primary exchange.
    """
    MARKET_HOURS = "market_hours"
    EXTENDED_HOURS = "extended_hours"
    CONTINUOUS = "continuous"
    
class PNLReset(str, Enum):
    """
    pnl_reset defines how we are calculating the baseline values for Profit And Loss (pnl) for queries with timeframe less than 1D (intraday queries).

    The default behavior for intraday queries is that we reset the pnl value to the previous day's closing equity for each trading day.

    In case of crypto (given it's continous nature), this might not be desired: specifying "no_reset" disables this behavior and all pnl values
    returned will be relative to the closing equity of the previous trading day.

    For 1D resolution all PnL values are calculated relative to the base_value, we are not reseting the base value.
    """
    PER_DAY = "per_day"
    NO_RESET = "no_reset"
    
class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
    
class OrderSide(str, Enum):
    """Buy or Sell order direction."""
    BUY = "buy"      # Buy side of the trade
    SELL = "sell"    # Sell side of the trade


class OrderType(str, Enum):
    """
    Type of order to place.
    
    The following provides a comprehensive breakdown of the supported order types for each category:

    - Equity trading: market, limit, stop, stop_limit, trailing_stop.
    - Options trading: market, limit, stop, stop_limit.
    - Multileg Options trading: market, limit.
    - Crypto trading: market, limit, stop_limit.
    ---
    - MARKET: Execute immediately at market price
    - LIMIT: Set your own price
    - STOP: Becomes market order at trigger price
    - STOP_LIMIT: Becomes limit order at trigger price
    - TRAILING_STOP: Trails market price with a stop
    """
    MARKET = "market"             # Executes immediately at market price
    LIMIT = "limit"               # Executes at a specific price or better
    STOP = "stop"                 # Becomes a market order when stop_price is hit
    STOP_LIMIT = "stop_limit"     # Becomes a limit order when stop_price is hit
    TRAILING_STOP = "trailing_stop"  # Adjusts with market price offset


class TimeInForce(str, Enum):
    """
    Duration the order remains active.
    
    Here is a breakdown of the supported TIFs for each specific security type:

    - Equity trading: day, gtc, opg, cls, ioc, fok.
    - Options trading: day.
    - Crypto trading: gtc, ioc.
    ---
    - DAY: Valid for the trading day

        A day order is eligible for execution only on the day it is live. 
        By default, the order is only valid during Regular Trading Hours (9:30am - 4:00pm ET). 
        If unfilled after the closing auction, it is automatically canceled. 
        If submitted after the close, it is queued and submitted the following trading day. 
        However, if marked as eligible for extended hours, the order can also execute during supported extended hours.
        
    - GTC: Good till canceled
    
        The order is good until canceled. 
        Non-marketable GTC limit orders are subject to price adjustments to offset corporate actions affecting the issue. 
        We do not currently support Do Not Reduce(DNR) orders to opt out of such price adjustments.
        
    - OPG: Executes in the market opening auction
    
        Use this TIF with a market/limit order type to submit “market on open” (MOO) and “limit on open” (LOO) orders. 
        This order is eligible to execute only in the market opening auction.
        Any unfilled orders after the open will be cancelled. 
        OPG orders submitted after 9:28am but before 7:00pm ET will be rejected. 
        OPG orders submitted after 7:00pm will be queued and routed to the following day’s opening auction. 
        On open/on close orders are routed to the primary exchange. 
        Such orders do not necessarily execute exactly at 9:30am / 4:00pm ET but execute per the exchange’s auction rules.
        
    - CLS: Executes in the market closing auction
    
        Use this TIF with a market/limit order type to submit “market on close” (MOC) and “limit on close” (LOC) orders. 
        This order is eligible to execute only in the market closing auction. 
        Any unfilled orders after the close will be cancelled. 
        CLS orders submitted after 3:50pm but before 7:00pm ET will be rejected. 
        CLS orders submitted after 7:00pm will be queued and routed to the following day’s closing auction. 
        Only available with API v2.
        
    - IOC: Fill immediately or cancel
    
        An Immediate Or Cancel (IOC) order requires all or part of the order to be executed immediately. 
        Any unfilled portion of the order is canceled. Only available with API v2. 
        Most market makers who receive IOC orders will attempt to fill the order on a principal basis only, and cancel any unfilled balance. 
        On occasion, this can result in the entire order being cancelled if the market maker does not have any existing inventory of the security in question.
        
    - FOK: Fill entirely or cancel
    
        A Fill or Kill (FOK) order is only executed if the entire order quantity can be filled, otherwise the order is canceled. 
        Only available with API v2.
        
    """
    DAY = "day"       # Active for current trading day only
    GTC = "gtc"       # Stays active until manually canceled
    OPG = "opg"       # Market or limit on open
    CLS = "cls"       # Market or limit on close
    IOC = "ioc"       # Immediate or cancel
    FOK = "fok"       # Fill or kill (entire quantity must fill or cancel)


class OrderStatusFilter(str, Enum):
    """
    Status of an order.

    - OPEN: Order is currently active
    - CLOSED: Order has completed or been canceled
    - ALL: Fetch orders of all statuses
    """
    OPEN = "open"       # Order is active and unfilled
    CLOSED = "closed"   # Order is filled or canceled
    ALL = "all"         # Match any order status


class OrderClass(str, Enum):
    """
    Type of complex order behavior (mostly for conditional/multi-leg orders).

    - SIMPLE: Regular single order
    - BRACKET: Includes take-profit and stop-loss legs
    - OTO: One Triggers Other (sequential)
    - OCO: One Cancels Other (conditional)
    - MLEG: Multileg strategy (used for options)
    """
    SIMPLE = "simple"     # Single-leg order
    BRACKET = "bracket"   # Includes take-profit and stop-loss
    OTO = "oto"           # One Triggers Other
    OCO = "oco"           # One Cancels Other
    MLEG = "mleg"         # Multi-leg options strategy

class PositionIntent(str, Enum):
    """
    - BUY_TO_OPEN: 
    - BUY_TO_CLOSE: 
    - SELL_TO_OPEN: 
    - SELL_TO_CLOSE: 
    """
    
    BUY_TO_OPEN = "buy_to_open"     
    BUY_TO_CLOSE = "buy_to_close"     
    SELL_TO_OPEN = "sell_to_open"     
    SELL_TO_CLOSE = "sell_to_close"     
    
class OrderStatus(str, Enum):
    """
    Represents the lifecycle status of an order executed through Alpaca.

    Common Statuses:
    ----------------
    - new:
        The order has been received by Alpaca and routed to exchanges for execution.
    - partially_filled:
        The order has been partially filled.
    - filled:
        The order has been completely filled; no further updates will occur.
    - done_for_day:
        The order is done executing for the day and will not update until the next session.
    - canceled:
        The order was canceled, either by the user or exchange.
    - expired:
        The order expired based on its time-in-force.
    - replaced:
        The order was replaced by another (e.g., updated).
    - pending_cancel:
        A cancel request has been made and is waiting to be processed.
    - pending_replace:
        A replacement order is pending. Cancel requests will be rejected in this state.

    Rare Statuses:
    --------------
    - accepted:
        Received by Alpaca but not yet routed (common outside market hours).
    - pending_new:
        Routed but not yet accepted by the exchanges.
    - accepted_for_bidding:
        Order received by exchanges and being evaluated for pricing.
    - stopped:
        A trade is guaranteed but has not occurred yet, usually at a specified price or better.
    - rejected:
        The order has been rejected by the broker or exchange.
    - suspended:
        The order is suspended and cannot be traded.
    - calculated:
        Execution is complete, but settlement calculations are still pending.
    """

    # Common statuses
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    DONE_FOR_DAY = "done_for_day"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REPLACED = "replaced"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"

    # Rare statuses
    ACCEPTED = "accepted"
    PENDING_NEW = "pending_new"
    ACCEPTED_FOR_BIDDING = "accepted_for_bidding"
    STOPPED = "stopped"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    CALCULATED = "calculated"
    
    def description(self) -> str:
        """Returns a human-readable explanation for each status."""
        return {
            self.NEW: "The order has been received by Alpaca and routed to exchanges for execution.",
            self.PARTIALLY_FILLED: "The order has been partially filled.",
            self.FILLED: "The order has been filled; no further updates will occur.",
            self.DONE_FOR_DAY: "The order is done executing for the day; no more updates until the next trading session.",
            self.CANCELED: "The order was canceled and will not update further.",
            self.EXPIRED: "The order expired due to time-in-force or session end.",
            self.REPLACED: "The order was replaced by another, typically due to an update.",
            self.PENDING_CANCEL: "The order is awaiting cancellation.",
            self.PENDING_REPLACE: "The order is awaiting replacement and cannot be canceled at this moment.",
            self.ACCEPTED: "The order has been received by Alpaca but has not been routed yet (common outside trading hours).",
            self.PENDING_NEW: "The order is routed but not yet accepted for execution.",
            self.ACCEPTED_FOR_BIDDING: "The order is being evaluated by exchanges for pricing.",
            self.STOPPED: "A guaranteed trade is coming, typically at or better than a stated price.",
            self.REJECTED: "The order has been rejected and will not proceed.",
            self.SUSPENDED: "The order is suspended and not eligible for trading.",
            self.CALCULATED: "Order execution complete, but financial settlement is still being processed.",
        }.get(self, "Unknown status")    