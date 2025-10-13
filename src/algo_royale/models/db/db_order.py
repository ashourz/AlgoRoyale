from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DBOrder(BaseModel):
    """
    Represents a database order in the Algo Royale system.

    Attributes:
        id (int): Unique identifier for the order.
        user_id (int): Identifier for the user who placed the order.
        account_id (int): Identifier for the account associated with the order.
        symbol (str): Trading symbol of the asset.
        market (str): Market where the order was placed.
        order_type (str): Type of the order (e.g., 'market', 'limit').
        status (str): Current status of the order (e.g., 'open', 'filled', 'cancelled').
        action (str): Action taken in the order (e.g., 'buy', 'sell').
        quantity (int): Number of shares in the order.
        price (float): Price per share for the order.
        created_at (datetime): Timestamp when the order was created.
        updated_at (datetime): Timestamp when the order was last updated.
    """

    id: UUID
    user_id: str
    account_id: str
    symbol: str
    market: str
    order_type: str
    status: str
    action: str
    settled: bool
    notional: float | None
    quantity: float | None
    price: float | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def columns(cls):
        """
        Returns a list of column names for the DBOrder model.
        This is useful for database operations where column names are needed.
        """
        return [
            "id",
            "user_id",
            "account_id",
            "symbol",
            "market",
            "order_type",
            "status",
            "action",
            "settled",
            "notional",
            "quantity",
            "price",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def from_tuple(cls, data: tuple) -> "DBOrder":
        """
        Creates a DBOrder object from a tuple of raw data.

        Args:
            data (tuple): A tuple representing an order with fields in the order defined by columns().

        Returns:
            DBOrder: An instance of DBOrder with fields populated from the tuple.
        """
        d = dict(zip(cls.columns(), data))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data: dict) -> "DBOrder":
        """
        Creates a DBOrder object from raw data.

        Args:
            data (dict): A dictionary representing an order from the database.
        Returns:
            DBOrder: An instance of DBOrder with fields populated from the raw data.
        """
        return DBOrder(
            id=data["id"],
            user_id=data["user_id"],
            account_id=data["account_id"],
            symbol=data["symbol"],
            order_type=data["order_type"],
            status=data["status"],
            action=data["action"],
            settled=bool(data["settled"]),
            notional=data["notional"],
            quantity=data["quantity"],
            price=data["price"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at", data["created_at"]),
        )
