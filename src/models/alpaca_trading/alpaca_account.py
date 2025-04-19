# src/models/alpaca_models/alpaca_account.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dateutil.parser import isoparse

class AccountStatus(Enum):
    ONBOARDING =  "ONBOARDING"                  #	The account is onboarding.
    SUBMISSION_FAILED =  "SUBMISSION_FAILED"    # The account application submission failed for some reason.
    SUBMITTED =  "SUBMITTED"                    # The account application has been submitted for review.
    ACCOUNT_UPDATED =  "ACCOUNT_UPDATED"        # The account information is being updated.
    APPROVAL_PENDING =  "APPROVAL_PENDING"      # The final account approval is pending.
    ACTIVE =  "ACTIVE"                          #	The account is active for trading.
    REJECTED =  "REJECTED"                      # The account application has been rejected.

class Account(BaseModel):
    id: str
    account_number: str
    status: AccountStatus
    crypto_status: AccountStatus
    currency: str
    cash: str
    portfolio_value: Optional[str]
    non_marginable_buying_power: str
    accrued_fees: str
    pending_transfer_in: str
    pending_transfer_out: str
    pattern_day_trader: bool
    trade_suspended_by_user: bool
    trading_blocked: bool
    transfers_blocked: bool
    account_blocked: bool
    created_at: datetime
    shorting_enabled: bool
    long_market_value: str
    short_market_value: str
    equity: str
    last_equity: str
    multiplier: str
    buying_power: str
    initial_margin: str
    maintenance_margin: str
    sma: str
    daytrade_count: int
    last_maintenance_margin: str
    daytrading_buying_power: str
    regt_buying_power: str

    @staticmethod
    def from_raw(data: dict) -> "Account":
        """
        Convert raw data from Alpaca API response into an Account object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            Account: An Account object populated with values from the raw data.
        """
        return Account(
            id=data["id"],
            account_number=data["account_number"],
            status=data["status"],
            crypto_status=data["crypto_status"],
            currency=data["currency"],
            cash=data["cash"],
            portfolio_value=data.get("portfolio_value"),
            non_marginable_buying_power=data["non_marginable_buying_power"],
            accrued_fees=data["accrued_fees"],
            pending_transfer_in=data.get("pending_transfer_in", "0"),
            pending_transfer_out=data.get("pending_transfer_out", "0"),
            pattern_day_trader=data["pattern_day_trader"],
            trade_suspended_by_user=data["trade_suspended_by_user"],
            trading_blocked=data["trading_blocked"],
            transfers_blocked=data["transfers_blocked"],
            account_blocked=data["account_blocked"],
            created_at=isoparse(data["created_at"]),
            shorting_enabled=data["shorting_enabled"],
            long_market_value=data["long_market_value"],
            short_market_value=data["short_market_value"],
            equity=data["equity"],
            last_equity=data["last_equity"],
            multiplier=data["multiplier"],
            buying_power=data["buying_power"],
            initial_margin=data["initial_margin"],
            maintenance_margin=data["maintenance_margin"],
            sma=data["sma"],
            daytrade_count=data["daytrade_count"],
            last_maintenance_margin=data["last_maintenance_margin"],
            daytrading_buying_power=data["daytrading_buying_power"],
            regt_buying_power=data["regt_buying_power"]
        )