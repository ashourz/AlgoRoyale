from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DBTrade(BaseModel):
    """
    Represents a trade in the Algo Royale system.

    Attributes:
        id (UUID): Unique identifier for the trade.
        external_id (str): Original ID from the external system (e.g., Alpaca).
        user_id (str): Identifier for the user who made the trade.
        account_id (str): Identifier for the account associated with the trade.
        symbol (str): Trading symbol of the asset.
        market (str): Market where the trade was executed.
        action (str): Action taken in the trade (e.g., 'buy', 'sell').
        settled (bool): Indicates if the trade has been settled.
        settlement_date (datetime): Date when the trade was settled, if applicable.
        price (float): Execution price of the trade.
        quantity (int): Number of shares traded.
        executed_at (datetime): Timestamp when the trade was executed.
        created_at (datetime): Timestamp when the trade record was created.
        order_id (UUID): ID of the associated order.
        updated_at (datetime): Timestamp when the trade record was last updated.
    """

    id: UUID
    external_id: str  # To store the original ID from the external system
    user_id: str
    account_id: str
    symbol: str
    action: str
    settled: bool = False
    settlement_date: datetime
    price: float
    quantity: float
    executed_at: datetime
    created_at: datetime
    order_id: UUID
    updated_at: datetime | None = None

    @classmethod
    def columns(cls):
        """
        Returns a list of column names for the DBTrade model.
        This is useful for database operations where column names are needed.
        """
        return [
            "id",
            "external_id",
            "user_id",
            "account_id",
            "symbol",
            "action",
            "settled",
            "settlement_date",
            "price",
            "quantity",
            "executed_at",
            "created_at",
            "order_id",
            "updated_at",
        ]

    @classmethod
    def from_tuple(cls, data: tuple) -> "DBTrade":
        """
        Creates a DBTrade object from raw data.

        Args:
            data (tuple): A tuple representing a trade from the database.

        Returns:
            DBTrade: An instance of DBTrade with fields populated from the raw data.
        """
        d = dict(zip(cls.columns(), data))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data: dict) -> "DBTrade":
        """
        Creates a DBTrade object from raw data.

        Args:
            data (dict): A dictionary representing a trade from the database.

        Returns:
            DBTrade: An instance of DBTrade with fields populated from the raw data.
        """
        return DBTrade(
            id=data["id"],
            external_id=data["external_id"],
            user_id=data["user_id"],
            account_id=data["account_id"],
            symbol=data["symbol"],
            action=data["action"],
            settled=bool(data["settled"]),
            settlement_date=data.get("settlement_date"),
            price=data["price"],
            quantity=data["quantity"],
            executed_at=data["executed_at"],
            created_at=data["created_at"],
            order_id=data["order_id"],
            updated_at=data.get("updated_at"),
        )
