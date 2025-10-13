from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DBDataStreamSession(BaseModel):
    """
    Represents a data stream session in the Algo Royale system.

    Attributes:
        id (UUID): Unique identifier for the session.
        stream_type (str): Type of the data stream (e.g., "trade", "order").
        symbol (str): Trading symbol for the data stream.
        strategy_name (str): Name of the trading strategy.
        start_time (datetime): Start time of the data stream session.
        end_time (datetime): End time of the data stream session.
    """

    id: UUID
    stream_type: str
    symbol: str
    strategy_name: str
    start_time: datetime
    end_time: Optional[datetime] = None

    @classmethod
    def columns(cls):
        """
        Returns a list of column names for the DBDataStreamSession model.
        This is useful for database operations where column names are needed.
        """
        return [
            "id",
            "stream_type",
            "symbol",
            "strategy_name",
            "start_time",
            "end_time",
        ]

    @classmethod
    def from_tuple(cls, data: tuple) -> "DBDataStreamSession":
        """
        Creates a DBDataStreamSession object from raw data.

        Args:
            data (tuple): A tuple representing a data stream session from the database.

        Returns:
            DBDataStreamSession: An instance of DBDataStreamSession with fields populated from the raw data.
        """
        d = dict(zip(cls.columns(), data))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data: dict) -> "DBDataStreamSession":
        """
        Creates a DBDataStreamSession object from raw data.

        Args:
            data (dict): A dictionary representing a data stream session from the database.

        Returns:
            DBDataStreamSession: An instance of DBDataStreamSession with fields populated from the raw data.
        """
        return DBDataStreamSession(
            id=data["id"],
            stream_type=data["stream_type"],
            symbol=data["symbol"],
            strategy_name=data["strategy_name"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
        )
