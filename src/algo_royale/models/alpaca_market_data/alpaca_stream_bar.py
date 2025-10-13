from pydantic import BaseModel


class StreamBar(BaseModel):
    """
    Represents a streaming stock bar update received via Alpaca's WebSocket.
    Attributes:
        symbol (str): The ticker symbol of the asset.
        volume (int): The trading volume for the bar.
        accumulated_volume (int): The total volume accumulated for the asset.
        official_open_price (float): The official opening price of the asset.
        vwap (float): The volume-weighted average price of the asset.
        open_price (float): The opening price of the asset.
        high_price (float): The highest price of the asset during the bar.
        low_price (float): The lowest price of the asset during the bar.
        close_price (float): The closing price of the asset.
        average_price (float): The average price of the asset during the bar.
        opening_epoch (int): The opening timestamp of the bar.
        closing_epoch (int): The closing timestamp of the bar.
    """

    symbol: str
    volume: int
    accumulated_volume: int
    official_open_price: float
    vwap: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    average_price: float
    opening_epoch: int
    closing_epoch: int

    @staticmethod
    def from_raw(data: dict) -> "StreamBar":
        """
        Convert raw WebSocket message from Alpaca into a StreamBar instance.

        Args:
            data (dict): Raw streaming bar dictionary from Alpaca.

        Returns:
            StreamBar: Parsed bar model.
        """
        return StreamBar(
            symbol=data["T"],
            volume=data["v"],
            accumulated_volume=data["av"],
            official_open_price=data["op"],
            vwap=data["vw"],
            open_price=data["o"],
            high_price=data["h"],
            low_price=data["l"],
            close_price=data["c"],
            average_price=data["a"],
            opening_epoch=data["s"],
            closing_epoch=data["e"],
        )
