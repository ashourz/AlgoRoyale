from datetime import datetime

from pydantic import BaseModel


class DBDataStreamSession(BaseModel):
    """
    Represents a data stream session in the Algo Royale system.

    Attributes:
        id (int): Unique identifier for the session.
        user_id (int): Identifier for the user associated with the session.
        account_id (int): Identifier for the account associated with the session.
        session_token (str): Token used to authenticate the session.
        created_at (datetime): Timestamp when the session was created.
        updated_at (datetime): Timestamp when the session was last updated.
    """

    id: int
    stream_type: str
    symbol: str
    strategy_name: str
    start_time: datetime
    end_time: datetime = None

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
    def from_dict(data: dict) -> "DBDataStreamSession":
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
