# src/models/alpaca_models/alpaca_corporate_action.py

from datetime import datetime
from typing import Dict, Optional

from dateutil.parser import isoparse  # if not using built-in parsing
from pydantic import BaseModel


class CorporateAction(BaseModel):
    """
    Represents a corporate action related to a stock symbol.

    Attributes:
        TODO: MISSING ATTRIBUTES

        action (str): The type of corporate action (e.g., "cash_dividend", "stock_split").
        cash_amount (float): The amount of cash involved in the action.
        cash_per_share (float): The amount of cash per share involved in the action.
        ex_date (datetime): The date when the action becomes effective.
        foreign (bool): Indicates if the action is foreign.
        payable_date (datetime): The date when the payment will be made.
        process_date (datetime): The date when the action will be processed.
        rate (float): The rate associated with the action.
        record_date (datetime): The date of record for the action.
        special (bool): Indicates if the action is special.
        symbol (str): The stock symbol associated with the action.
    """

    ex_date: datetime
    foreign: bool
    payable_date: datetime
    process_date: datetime
    rate: float
    record_date: datetime
    special: bool
    symbol: str

    @staticmethod
    def from_raw(data: dict) -> "CorporateAction":
        """
        Convert raw data from Alpaca API response into a CorporateAction object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            CorporateAction: A CorporateAction object populated with values from the raw data.

        Example:
            data = {
                "action": "cash_dividend",
                "cash_amount": 1.00,
                "cash_per_share": 0.50,
                "ex_date": "2024-04-01T00:00:00Z",
                "foreign": False,
                "payable_date": "2024-04-15T00:00:00Z",
                "process_date": "2024-04-16T00:00:00Z",
                "rate": 0.5,
                "record_date": "2024-03-31T00:00:00Z",
                "special": False,
                "symbol": "AAPL"
            }
            corporate_action = CorporateAction.from_raw(data)
        """

        return CorporateAction(
            ex_date=isoparse(data["ex_date"]),
            foreign=data.get("foreign", False),
            payable_date=isoparse(data["payable_date"]),
            process_date=isoparse(data["process_date"]),
            rate=data.get("rate", 0.0),
            record_date=isoparse(data["record_date"]),
            special=data.get("special", False),
            symbol=data["symbol"],
        )


class CorporateActionResponse(BaseModel):
    """
    Represents the response from the Alpaca API when fetching corporate actions.

    Attributes:
        corporate_actions (Dict[str, list[CorporateAction]]): A dictionary where the keys are symbol tickers (e.g., "AAPL") and the values are lists of `CorporateAction` objects for that symbol.
        next_page_token (Optional[str]): Token for pagination if more data is available.
    """

    corporate_actions: Dict[
        str, list[CorporateAction]
    ]  # Mapping of symbol (str) to list of Corporate objects
    next_page_token: Optional[str]  # Token for pagination if more data is available

    @classmethod
    def from_raw(cls, data: dict) -> Optional["CorporateActionResponse"]:
        """
        Convert raw data from Alpaca API response into a CorporateActionResponse object.

        Attrs:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            CorporateActionResponse: A CorporateActionResponse object populated with values from the raw data.
        """

        if not data or "corporate_actions" not in data:
            return None

        return cls(
            corporate_actions={
                symbol: [
                    CorporateAction.from_raw(ca)
                    for ca in (action if isinstance(action, list) else [action])
                ]
                for symbol, action in data["corporate_actions"].items()
            },
            next_page_token=data.get("next_page_token"),
        )


class CorporateActionListResponse(BaseModel):
    corporate_actions: list[CorporateAction]

    @classmethod
    def from_raw(cls, data: dict) -> Optional["CorporateActionListResponse"]:
        """
        Convert raw data from Alpaca API response into a flat list of CorporateAction objects.
        """
        if not data or "corporate_actions" not in data:
            return None

        flat_actions = []
        for actions in data["corporate_actions"].values():
            flat_actions.extend(
                [
                    CorporateAction.from_raw(ca)
                    for ca in (actions if isinstance(actions, list) else [actions])
                ]
            )

        return cls(corporate_actions=flat_actions)
