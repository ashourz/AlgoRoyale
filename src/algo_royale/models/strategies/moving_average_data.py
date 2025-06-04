# strategies/models/moving_average_data.py

from decimal import Decimal

import pandas as pd
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class MovingAverageData(BaseModel):
    """
    A data model specific to the Moving Average strategy.
    It expects historical data with fields necessary to calculate moving averages.
    """

    close: Annotated[
        Decimal, Field(strict=True, allow_inf_nan=True)
    ]  # 'close' price of the asset

    @classmethod
    def to_dataframe(cls, data: list[dict]) -> pd.DataFrame:
        """
        Converts a list of MovingAverageData objects into a pandas DataFrame.
        Ensures that the data is properly validated before conversion.
        """
        valid_data = [
            item.dict() for item in data
        ]  # Call the 'dict' method of the instance directly
        return pd.DataFrame(valid_data)
