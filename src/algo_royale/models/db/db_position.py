from pydantic import BaseModel


class DBPosition(BaseModel):
    """
    Represents a position in the database.

    Attributes:
        symbol (str): The stock symbol of the position.
        market (str): The market where the position is held (e.g., 'NYSE', 'NASDAQ').
        user_id (int): The ID of the user who owns the position.
        account_id (int): The ID of the account associated with the position.
        net_position (float): The net position of the stock in the account.
    """

    symbol: str
    market: str
    user_id: int
    account_id: int
    net_position: float

    @classmethod
    def columns(cls):
        return [
            "symbol",
            "market",
            "user_id",
            "account_id",
            "net_position",
        ]

    @classmethod
    def from_tuple(cls, data: tuple) -> "DBPosition":
        """
        Create a DBPosition instance from a tuple.
        """
        d = dict(zip(cls.columns(), data))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data: dict) -> "DBPosition":
        """
        Create a DBPosition instance from a dictionary.
        """
        return cls(
            symbol=data["symbol"],
            market=data["market"],
            account_id=data["account_id"],
            net_position=data["net_position"],
        )
