# src/models/alpaca_models/alpaca_account.py

from enum import Enum
from shared.models.alpaca_trading.enums import ActivityType, DTBPCheck, MarginMultiplier, OptionsTradingLevel, OrderSide, PDTCheck, TradeActivityType, TradeConfirmationEmail
from pydantic import BaseModel
from typing import List, Optional
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


class AccountConfiguration(BaseModel):
    dtbp_check: Optional[DTBPCheck] = None
    fractional_trading: Optional[bool] = None
    max_margin_multiplier: Optional[MarginMultiplier] = None
    max_options_trading_level: Optional[OptionsTradingLevel] = None
    no_shorting: Optional[bool] = None
    pdt_check: Optional[PDTCheck] = None
    ptp_no_exception_entry: Optional[bool] = None
    suspend_trade: Optional[bool] = None
    trade_confirm_email: Optional[TradeConfirmationEmail] = None

    @staticmethod
    def from_raw(data: dict) -> "AccountConfiguration":
        """
        Convert raw data from Alpaca API response into an AccountConfiguration object.

        Args:
            data (dict): The raw data returned from Alpaca API.

        Returns:
            AccountConfiguration: An AccountConfiguration object populated with values from the raw data.
        """
        return AccountConfiguration(
            dtbp_check=DTBPCheck(data["dtbp_check"]) if "dtbp_check" in data else None,
            fractional_trading=data.get("fractional_trading"),
            max_margin_multiplier=MarginMultiplier(data["max_margin_multiplier"]) if "max_margin_multiplier" in data else None,
            max_options_trading_level=OptionsTradingLevel(data["max_options_trading_level"]) if "max_options_trading_level" in data else None,
            no_shorting=data.get("no_shorting"),
            pdt_check=PDTCheck(data["pdt_check"]) if "pdt_check" in data else None,
            ptp_no_exception_entry=data.get("ptp_no_exception_entry"),
            suspend_trade=data.get("suspend_trade"),
            trade_confirm_email=TradeConfirmationEmail(data["trade_confirm_email"]) if "trade_confirm_email" in data else None
        )

        
class AccountActivity(BaseModel):
    activity_type: Optional[ActivityType] = None
    id: Optional[str] = None
    cum_qty: Optional[str] = None
    leaves_qty: Optional[str] = None
    price: Optional[str] = None
    qty: Optional[str] = None
    side: Optional[OrderSide] = None
    symbol: Optional[str] = None
    transaction_time: Optional[datetime] = None
    order_id: Optional[str] = None
    type: Optional[TradeActivityType] = None
    order_status: Optional[str] = None
    # Additional optional fields
    date: Optional[str] = None
    net_amount: Optional[str] = None
    per_share_amount: Optional[str] = None

    @staticmethod
    def from_raw(data: dict) -> "AccountActivity":
        return AccountActivity(
            activity_type=ActivityType(data["activity_type"]) if "activity_type" in data else None,
            id=data.get("id", None),
            cum_qty=data.get("cum_qty", None),
            leaves_qty=data.get("leaves_qty", None),
            price=data.get("price", None),
            qty=data.get("qty", None),
            side=OrderSide(data["side"]) if "side" in data else None,
            symbol=data.get("symbol", None),
            transaction_time=datetime.fromisoformat(data["transaction_time"].replace("Z", "+00:00")) if "transaction_time" in data else None,
            order_id=data.get("order_id", None),
            type=TradeActivityType(data["type"]) if "type" in data else None,
            order_status=data.get("order_status", None),
            # Additional fields
            date=data.get("date", None),
            net_amount=data.get("net_amount", None),
            per_share_amount=data.get("per_share_amount", None),
        )


class AccountActivities(BaseModel):
    activities: List[AccountActivity]

    @staticmethod
    def from_raw(data: List[dict]) -> "AccountActivities":
        return AccountActivities(
            activities=[AccountActivity.from_raw(item) for item in data]
        )