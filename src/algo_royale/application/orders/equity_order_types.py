from typing import Literal

from pydantic import BaseModel, model_validator

from algo_royale.application.orders.equity_order_enums import (
    EquityOrderClass,
    EquityOrderSide,
    EquityOrderType,
    EquityTimeInForce,
)


class EquityBaseOrder(BaseModel):
    """
    Base order for equity trades.

    Attributes:
        symbol (str): The trading symbol (e.g., 'AAPL').
        side (EquityOrderSide): Buy or sell side of the order.
        order_type (EquityOrderType): Type of order (e.g., market, limit).
        order_class (EquityOrderClass): Class of order (e.g., simple, bracket). Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force for order validity. Default is DAY.
        extended_hours (bool): Whether order is eligible for extended hours. Default is False.
        client_order_id (str | None): Optional unique client order ID.
    """

    symbol: str
    side: EquityOrderSide
    order_type: EquityOrderType
    order_class: EquityOrderClass = EquityOrderClass.SIMPLE
    time_in_force: EquityTimeInForce = EquityTimeInForce.DAY
    extended_hours: bool = False
    client_order_id: str | None = None


class EquityMarketQtyOrder(EquityBaseOrder):
    """
    Market order with quantity-based execution.

    Attributes:
        symbol (str): The trading symbol (e.g., 'AAPL').
        side (EquityOrderSide): Buy or sell side of the order.
        order_type (Literal[MARKET]): Fixed as 'market'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force for order validity. Default is DAY.
        extended_hours (bool): Whether order is eligible for extended hours. Default is False.
        client_order_id (str | None): Optional unique client order ID.
        quantity (float): Number of shares to buy or sell.
    """

    quantity: float
    order_type: Literal[EquityOrderType.MARKET] = EquityOrderType.MARKET


class EquityMarketNotionalOrder(EquityBaseOrder):
    """
    Market order using notional (dollar) value.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[MARKET]): Fixed as 'market'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force. Default is DAY.
        extended_hours (bool): Allow after/premarket. Default is False.
        client_order_id (str | None): Optional ID.
        notional (float): Dollar amount to trade.
    """

    notional: float
    order_type: Literal[EquityOrderType.MARKET] = EquityOrderType.MARKET


class EquityLimitOrder(EquityBaseOrder):
    """
    Limit order to buy or sell at a specific price or better.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[LIMIT]): Fixed as 'limit'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force. Default is DAY.
        extended_hours (bool): Allow after/premarket. Default is False.
        client_order_id (str | None): Optional ID.
        quantity (float): Number of shares.
        limit_price (float): Price threshold for the order.
    """

    quantity: float
    limit_price: float
    order_type: Literal[EquityOrderType.LIMIT] = EquityOrderType.LIMIT


class EquityStopOrder(EquityBaseOrder):
    """
    Stop order that triggers a market order when stop price is reached.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[STOP]): Fixed as 'stop'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force. Default is DAY.
        extended_hours (bool): Allow after/premarket. Default is False.
        client_order_id (str | None): Optional ID.
        quantity (float): Number of shares.
        stop_price (float): Trigger price to activate the market order.
    """

    quantity: float
    stop_price: float
    order_type: Literal[EquityOrderType.STOP] = EquityOrderType.STOP


class EquityStopLimitOrder(EquityBaseOrder):
    """
    Stop-limit order that triggers a limit order when stop price is reached.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[STOP_LIMIT]): Fixed as 'stop_limit'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force. Default is DAY.
        extended_hours (bool): Allow after/premarket. Default is False.
        client_order_id (str | None): Optional ID.
        quantity (float): Number of shares.
        stop_price (float): Trigger price for limit order.
        limit_price (float): Price limit for the resulting order.
    """

    quantity: float
    stop_price: float
    limit_price: float
    order_type: Literal[EquityOrderType.STOP_LIMIT] = EquityOrderType.STOP_LIMIT


class EquityTrailingStopOrder(EquityBaseOrder):
    """
    Trailing stop order that moves with market price.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[TRAILING_STOP]): Fixed as 'trailing_stop'.
        order_class (EquityOrderClass): Order class. Default is SIMPLE.
        time_in_force (EquityTimeInForce): Time in force. Default is DAY.
        extended_hours (bool): Allow after/premarket. Default is False.
        client_order_id (str | None): Optional ID.
        quantity (float): Number of shares.
        trail_price (float | None): Fixed dollar offset from market.
        trail_percent (float | None): Percentage offset from market.
    """

    quantity: float
    trail_price: float | None = None
    trail_percent: float | None = None
    order_type: Literal[EquityOrderType.TRAILING_STOP] = EquityOrderType.TRAILING_STOP

    @model_validator(mode="after")
    def validate_trailing_stop(cls, model):
        if not model.trail_price and not model.trail_percent:
            raise ValueError("Must specify either trail_price or trail_percent")
        return model


class BracketTakeProfit(BaseModel):
    """
    Take-profit leg of a bracket order.

    Attributes:
        limit_price (float): Price at which to take profit.
    """

    limit_price: float


class BracketStopLoss(BaseModel):
    """
    Stop-loss leg of a bracket order.

    Attributes:
        stop_price (float): Price to trigger stop-loss.
        limit_price (float | None): Optional price limit for stop-loss order.
    """

    stop_price: float
    limit_price: float | None = None


class EquityBracketOrder(EquityLimitOrder):
    """
    Bracket order with take-profit and stop-loss sub-orders.

    Attributes:
        symbol (str): The trading symbol.
        side (EquityOrderSide): Buy or sell.
        order_type (Literal[LIMIT]): Must be market or limit.
        order_class (Literal[BRACKET]): Fixed as 'bracket'.
        time_in_force (EquityTimeInForce): Time in force.
        extended_hours (bool): Allow extended hours.
        client_order_id (str | None): Optional ID.
        quantity (float): Number of shares.
        limit_price (float): Price for the entry order.
        take_profit (BracketTakeProfit): Take-profit configuration.
        stop_loss (BracketStopLoss): Stop-loss configuration.
    """

    order_class: EquityOrderClass = EquityOrderClass.BRACKET
    take_profit: BracketTakeProfit
    stop_loss: BracketStopLoss
