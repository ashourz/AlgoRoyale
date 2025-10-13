from pydantic import BaseModel

from algo_royale.application.orders.equity_order_enums import EquityOrderSide


class SignalOrderPayload(BaseModel):
    """
    Payload for signal-based order generation.

    Attributes:
        symbol (str): The stock symbol for which the order is generated.
        side (EquityOrderSide): The side of the order (buy/sell).
        weight (float): The weight of the order in the portfolio.
        price_data (dict): The price data for the order.
            - DataIngestColumns.PRICE
            - DataIngestColumns.TIMESTAMP
            - DataIngestColumns.OPEN_PRICE
            - DataIngestColumns.HIGH_PRICE
            - DataIngestColumns.LOW_PRICE
            - DataIngestColumns.CLOSE_PRICE
            - DataIngestColumns.VOLUME
            - DataIngestColumns.NUM_TRADES
            - DataIngestColumns.VOLUME_WEIGHTED_PRICE
    """

    symbol: str
    side: EquityOrderSide
    weight: float
    price_data: dict
