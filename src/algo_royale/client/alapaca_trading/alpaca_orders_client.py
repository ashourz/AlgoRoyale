# src/algo_royale/client/alpaca_corporate_action_client.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.client.exceptions import MissingParameterError, ParameterConflictError
from models.alpaca_trading.alpaca_order import DeleteOrdersResponse, OrderListResponse, Order, StopLoss, TakeProfit
from models.alpaca_trading.enums import OrderClass, OrderSide, OrderStatus, OrderStatusFilter, OrderType, PositionIntent, SortDirection, TimeInForce
from config.config import ALPACA_TRADING_URL

class AlpacaOrdersClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for trading corporate action data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaOrdersClient"    
    
    def create_order(
        self,
        symbol: Optional[str] = None,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        side: Optional[OrderSide] = None,
        order_type: Optional[OrderType] = None,
        time_in_force: Optional[TimeInForce] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
        extended_hours: Optional[bool] = None,
        client_order_id: Optional[str] = None,
        order_class: Optional[OrderClass] = None,
        take_profit: Optional[TakeProfit] = None,
        stop_loss: Optional[StopLoss] = None,
        position_intent: Optional[PositionIntent] = None
    ) -> Optional[Order]:
        """
        Create an order with the given parameters.

        Parameters:
            - symbol (str): The symbol or currency pair.
            - qty (float): Number of shares to trade. Can be fractional for market & day orders.
            - notional (float): Dollar amount to trade. Mutually exclusive with qty. Only for market + day orders.
            - side (OrderSide): 'buy' or 'sell'. Required for all order classes except mleg.
            - order_type (OrderType): The order types supported by Alpaca vary based on the order's security type. The following provides a comprehensive breakdown of the supported order types for each category:

                - Equity trading: market, limit, stop, stop_limit, trailing_stop.
                - Options trading: market, limit, stop, stop_limit.
                - Multileg Options trading: market, limit.
                - Crypto trading: market, limit, stop_limit.
                
            - time_in_force (TimeInForce): The Time-In-Force values supported by Alpaca vary based on the order's security type. 
            
                Here is a breakdown of the supported TIFs for each specific security type:
                - Equity trading: day, gtc, opg, cls, ioc, fok.
                - Options trading: day.
                - Crypto trading: gtc, ioc.
                
            - limit_price (float): Required if type is limit or stop_limit.
            
                In case of mleg, the limit_price parameter is expressed with the following notation:
                    - A positive value indicates a debit, representing a cost or payment to be made.
                    - A negative value signifies a credit, reflecting an amount to be received.

            - stop_price (float): Required for 'stop' or 'stop_limit'.
            - trail_price (float): Required (or trail_percent) for 'trailing_stop'.
            - trail_percent (float): Required (or trail_price) for 'trailing_stop'.
            - extended_hours (bool): (default) false. 
            
                If true, order will be eligible to execute in premarket/afterhours.
                Only works with type limit and time_in_force day..
            - client_order_id (str): Optional client-side ID (<= 128 chars).

                A unique identifier for the order. Automatically generated if not sent. (<= 128 characters)
                
            - order_class (OrderClass): The order classes supported by Alpaca vary based on the order's security type. The following provides a comprehensive breakdown of the supported order classes for each category:

                - Equity trading: simple (or ""), oco, oto, bracket.
                - Options trading:
                    - simple (or "")
                    - mleg (required for multi-leg complex option strategies)
                - Crypto trading: simple (or "")
                
            - take_profit (TakeProfit): Object with required `limit_price` for bracket/advanced orders.
            - stop_loss (StopLoss): Object with required `stop_price` and optional `limit_price`.
            - position_intent (PositionIntent): Positioning strategy for options (if supported).

        Returns:
            - OrderResponse object or None if no response.
        """

        # --- Basic validation ---
        if not symbol:
            raise MissingParameterError("Missing required parameter: 'symbol'.")

        if qty and notional:
            raise ParameterConflictError("Specify either 'qty' or 'notional', not both.")

        if not qty and not notional:
            raise MissingParameterError("You must specify either 'qty' or 'notional'.")

        if order_type in ["stop", "stop_limit"] and not stop_price:
            raise MissingParameterError(f"'stop_price' is required for order_type '{order_type}'.")

        if order_type in ["limit", "stop_limit"] and not limit_price:
            raise MissingParameterError(f"'limit_price' is required for order_type '{order_type}'.")

        if order_type == "trailing_stop":
            if not (trail_price or trail_percent):
                raise MissingParameterError("Either 'trail_price' or 'trail_percent' is required for 'trailing_stop' order.")
            if trail_price and trail_percent:
                raise ParameterConflictError("Specify only one: 'trail_price' or 'trail_percent' for 'trailing_stop'.")

        payload = {}

        # --- Build request payload ---
        if symbol:
            payload["symbol"] = symbol
        if qty:
            payload["qty"] = str(qty)
        if notional:
            payload["notional"] = str(notional)
        if side:
            payload["side"] = side
        if order_type:
            payload["type"] = order_type
        if time_in_force:
            payload["time_in_force"] = time_in_force
        if limit_price:
            payload["limit_price"] = str(limit_price)
        if stop_price:
            payload["stop_price"] = str(stop_price)
        if trail_price:
            payload["trail_price"] = str(trail_price)
        if trail_percent:
            payload["trail_percent"] = str(trail_percent)
        if extended_hours:
            payload["extended_hours"] = extended_hours
        if client_order_id:
            payload["client_order_id"] = client_order_id
        if order_class:
            payload["order_class"] = order_class
        if take_profit:
            payload["take_profit"] = take_profit.model_dump(exclude_unset=True)
        if stop_loss:
            payload["stop_loss"] = stop_loss.model_dump(exclude_unset=True)
        if position_intent:
            payload["position_intent"] = position_intent

        # Format all non-None parameters
        for k, v in payload.items():
            if v is not None:
                payload[k] = self._format_param(v)

        response_json = self._post(
            url=f"{self.base_url}/orders",
            payload=payload
        )

        if response_json is None:
            self._logger.warning("No order response received.")
            return None

        return Order.from_raw(response_json)
    
    def get_all_orders(
        self,
        status: Optional[OrderStatusFilter] = None, 
        limit: Optional[int] = None,
        after: Optional[datetime] = None,
        until: Optional[datetime] = None,
        direction: Optional[SortDirection] = None,
        nested: Optional[bool] = None,
        symbols: Optional[List[str]] = None,
        side: Optional[OrderSide] = None
    ) -> Optional[OrderListResponse]:
        """
        Get all orders with the given parameters.

        Parameters:
            - status (OrderStatusFilter) : Order status to be queried. open, closed or all. Defaults to open.
            - limit (int) : The maximum number of orders in response. Defaults to 50 and max is 500.
            - after (datetime) : The response will include only ones submitted after this timestamp (exclusive.)
            - until (datetime) : The response will include only ones submitted until this timestamp (exclusive.)
            - direction (SortDirection) : The chronological order of response based on the submission time. asc or desc. Defaults to desc.
            - nested (bool) : If true, the result will roll up multi-leg orders under the legs field of primary order.
            - symbols: (List[str]) : A comma-separated list of symbols to filter by (ex. “AAPL,TSLA,MSFT”). 
            - side (OrderSide) : 'buy' or 'sell'. Required for all order classes except mleg.

        Returns:
            - OrderListResponse object or None if no response.
        """

        params = {}

        # --- Build request payload ---
        if status:
            params["status"] = status
        if limit:
            params["limit"] = min(limit, 500)
        if after:
            params["after"] = after
        if until:
            params["until"] = until
        if direction:
            params["direction"] = direction
        if nested:
            params["nested"] = nested
        if symbols:
            params["symbols"] = ",".join(symbols),
        if side:
            params["side"] = side
        
        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)

        response_json = self._get(
            url=f"{self.base_url}/orders",
            params=params
        )

        if response_json is None:
            self._logger.warning("No order response received.")
            return None

        return OrderListResponse.from_raw(response_json)
    
    def get_order_by_client_order_id(
        self,
        client_order_id: str,
        nested: Optional[bool] = None,
    ) -> Optional[Order]:
        """
        Get order by client order id.

        Parameters:
            - client_order_id (str) :The client-assigned order ID.

        Returns:
            - OrderResponse object or None if no response.
        """
        params = {}
        params["client_order_id"] = client_order_id
        if nested:
            params["nested"] = nested
            
                # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response_json = self._get(
            url=f"{self.base_url}/orders:by_client_order_id",
            params = params
        )

        if response_json is None:
            self._logger.warning("No order response received.")
            return None

        return Order.from_raw(response_json)
    
    def replace_order_by_client_order_id(
        self,
        client_order_id: str,
        qty: Optional[int] = None,
        time_in_force: Optional[TimeInForce] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        new_client_order_id: Optional[str] = None
    ) -> Optional[Order]:
        """
        Get order by client order id.

        Parameters:
            - client_order_id (str) :The client-assigned order ID.
            - qty (float): Number of shares to trade. Can be fractional for market & day orders.
             - time_in_force (TimeInForce): The Time-In-Force values supported by Alpaca vary based on the order's security type. 
            
                Here is a breakdown of the supported TIFs for each specific security type:
                - Equity trading: day, gtc, opg, cls, ioc, fok.
                - Options trading: day.
                - Crypto trading: gtc, ioc.
                
            - limit_price (float): Required if type is limit or stop_limit.
            
                In case of mleg, the limit_price parameter is expressed with the following notation:
                    - A positive value indicates a debit, representing a cost or payment to be made.
                    - A negative value signifies a credit, reflecting an amount to be received.

            - stop_price (float): Required for 'stop' or 'stop_limit'.
            - trail_price (float): Required (or trail_percent) for 'trailing_stop'.
            - new_client_order_id (str): Optional client-side ID (<= 128 chars).

                A unique identifier for the order. Automatically generated if not sent. (<= 128 characters)
                
        Returns:
            - OrderResponse object or None if no response.
        """

        payload = {}

        # --- Build request payload ---
        if qty:
            payload["qty"] = str(qty)
        if time_in_force:
            payload["time_in_force"] = time_in_force
        if limit_price:
            payload["limit_price"] = str(limit_price)
        if stop_price:
            payload["stop_price"] = str(stop_price)
        if trail_price:
            payload["trail_price"] = str(trail_price)
        if new_client_order_id:
            payload["client_order_id"] = new_client_order_id

        # Format all non-None parameters
        for k, v in payload.items():
            if v is not None:
                payload[k] = self._format_param(v)

        response_json = self._patch(
            url=f"{self.base_url}/orders/{client_order_id}",
            payload=payload
        )

        if response_json is None:
            self._logger.warning("No order response received.")
            return None

        return Order.from_raw(response_json)
    
    def delete_order_by_client_order_id(
        self,
        client_order_id: str,
    ) -> Optional[DeleteOrdersResponse]:
        """
        Delete an order by its client_order_id.

        Returns:
            - None if the order was successfully deleted (204 No Content).
            - Raises ValueError if the order status is not cancelable (422).
            - Parsed JSON response in other cases.
        """
        response = self._delete(
            url=f"{self.base_url}/orders/{client_order_id}",
        )

        if response.status_code == 204:  # No Content - Order successfully deleted
            return None  # No content to return
        
        elif response.status_code == 422:  # Unprocessable Entity - Order cannot be canceled
            raise ValueError("The order status is not cancelable.")
        
        # If the status code is not 204 or 422, we return an error
        response.raise_for_status()  # This will raise an HTTPError for any 4xx/5xx status codes

        # Only try to parse the response as JSON if it's not empty
        if response.content:
            try:
                # Attempt to parse the response if there's any content
                response_json = response.json()
            except ValueError:
                response_json = None  # Return None if the response body is invalid JSON
        else:
            response_json = None  # No content to parse
        
        return response_json  # Return parsed JSON or None if there's no content
    
    def delete_all_orders(
        self
    ) -> Optional[DeleteOrdersResponse]:
        """
        Delete all orders.

        Returns:
            - DeleteOrdersResponse object or None if no response.
        """
        response_json = self._delete(
            url=f"{self.base_url}/orders"
        )

        if response_json is None:
            self._logger.warning("No order response received.")
            return None

        return DeleteOrdersResponse.from_raw(response_json) 
    
    