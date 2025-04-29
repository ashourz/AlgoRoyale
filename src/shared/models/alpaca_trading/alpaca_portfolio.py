from datetime import datetime
from typing import List
from pydantic import BaseModel


class PortfolioPerformance(BaseModel):
    """
    Represents the portfolio performance metrics over time from Alpaca.

    Attributes:
        timestamp (List[int]): List of Unix timestamps.
        equity (List[float]): List of equity values corresponding to each timestamp.
        profit_loss (List[float]): List of profit/loss values over time.
        profit_loss_pct (List[float]): List of profit/loss percentages over time.
        base_value (float): The initial value of the portfolio.
        timeframe (str): The timeframe for the data aggregation (e.g., '15Min').
        base_value_asof (datetime): The date as of which the base value applies.
    """

    timestamp: List[int]
    equity: List[float]
    profit_loss: List[float]
    profit_loss_pct: List[float]
    base_value: float
    timeframe: str
    base_value_asof: datetime

    @classmethod
    def from_raw(cls, data: dict) -> "PortfolioPerformance":
        """
        Converts raw API dictionary into a structured PortfolioPerformance object.

        Args:
            data (dict): The raw API dictionary.

        Returns:
            PortfolioPerformance: The parsed performance data model.
        """
        if isinstance(data.get("base_value_asof"), str):
            data["base_value_asof"] = datetime.fromisoformat(data["base_value_asof"])

        return cls(**data)