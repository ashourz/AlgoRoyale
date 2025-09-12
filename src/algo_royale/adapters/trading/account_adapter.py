from datetime import datetime
from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_accounts_client import (
    AlpacaAccountClient,
)
from algo_royale.clients.alpaca.exceptions import ParameterConflictError
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_account import (
    Account,
    AccountActivities,
    AccountConfiguration,
)
from algo_royale.models.alpaca_trading.enums.enums import (
    ActivityType,
    DTBPCheck,
    MarginMultiplier,
    OptionsTradingLevel,
    PDTCheck,
    SortDirection,
    TradeConfirmationEmail,
)


class AccountAdapter:
    """Service class to interact with Alpaca account data, leveraging the AlpacaAccountClient."""

    def __init__(self, account_client: AlpacaAccountClient, logger: Loggable):
        """
        Initializes AlpacaAccountService with the given AlpacaAccountClient.

        Args:
            account_client (AlpacaAccountClient): The Alpaca API client used to fetch data from the Alpaca API.
        """
        self.account_client = account_client
        self.logger = logger

    async def get_account_data(self) -> Optional[Account]:
        """
        Fetches account data from the Alpaca API.

        Returns:
            Optional[Account]: The account data retrieved from Alpaca, or None if no data is found.
        """
        return await self.account_client.fetch_account()

    async def get_account_configuration(self) -> Optional[AccountConfiguration]:
        """
        Fetches account configuration from the Alpaca API.

        Returns:
            Optional[AccountConfiguration]: The account configuration retrieved from Alpaca.
        """
        return await self.account_client.fetch_account_configuration()

    async def update_account_configuration(
        self,
        dtbp_check: Optional[DTBPCheck] = None,
        trade_confirm_email: Optional[TradeConfirmationEmail] = None,
        suspend_trade: Optional[bool] = None,
        no_shorting: Optional[bool] = None,
        fractional_trading: Optional[bool] = None,
        max_margin_multiplier: Optional[MarginMultiplier] = None,
        max_options_trading_level: Optional[OptionsTradingLevel] = None,
        pdt_check: Optional[PDTCheck] = None,
        ptp_no_exception_entry: Optional[bool] = None,
    ) -> Optional[AccountConfiguration]:
        """
        Updates and fetches account configuration from the Alpaca API.

        Args:
            dtbp_check (Optional[DTBPCheck]): Optional, to update the day trade buying power check.
            trade_confirm_email (Optional[TradeConfirmationEmail]): Optional, to set whether trade confirmations are sent by email.
            suspend_trade (Optional[bool]): Optional, to suspend trading for the account.
            no_shorting (Optional[bool]): Optional, to prevent shorting of stocks.
            fractional_trading (Optional[bool]): Optional, to enable/disable fractional trading.
            max_margin_multiplier (Optional[MarginMultiplier]): Optional, to set the maximum margin multiplier.
            max_options_trading_level (Optional[OptionsTradingLevel]): Optional, to set the max options trading level.
            pdt_check (Optional[PDTCheck]): Optional, to enable/disable pattern day trader check.
            ptp_no_exception_entry (Optional[bool]): Optional, to control exception entries in the pattern day trader check.

        Returns:
            Optional[AccountConfiguration]: The updated account configuration retrieved from Alpaca.
        """
        return await self.account_client.update_account_configuration(
            dtbp_check=dtbp_check,
            trade_confirm_email=trade_confirm_email,
            suspend_trade=suspend_trade,
            no_shorting=no_shorting,
            fractional_trading=fractional_trading,
            max_margin_multiplier=max_margin_multiplier,
            max_options_trading_level=max_options_trading_level,
            pdt_check=pdt_check,
            ptp_no_exception_entry=ptp_no_exception_entry,
        )

    async def get_account_activities(
        self,
        activity_types: Optional[list[ActivityType]] = None,
        category: Optional[str] = None,
        date: Optional[datetime] = None,
        until: Optional[datetime] = None,
        after: Optional[datetime] = None,
        direction: Optional[SortDirection] = SortDirection.DESC,
        page_size: Optional[int] = 100,
        page_token: Optional[str] = None,
    ) -> Optional[AccountActivities]:
        """
        Retrieves account activities from the Alpaca API.

        Args:
            activity_types (Optional[list[ActivityType]]): List of activity types to filter results.
            category (Optional[str]): Activity category (mutually exclusive with activity_types).
            date (Optional[datetime]): Specific date for filtering activities.
            until (Optional[datetime]): Filter activities before this date.
            after (Optional[datetime]): Filter activities after this date.
            direction (Optional[SortDirection]): 'asc' or 'desc', default is 'desc'.
            page_size (Optional[int]): Number of results to return per page, default is 100.
            page_token (Optional[str]): Token for pagination.

        Returns:
            Optional[AccountActivities]: A list of account activity objects or None if not found.
        """
        if activity_types and category:
            raise ParameterConflictError(
                "Specify either 'activity_types' or 'category' or neither, not both."
            )

        return await self.account_client.get_account_activities(
            activity_types=activity_types,
            category=category,
            date=date,
            until=until,
            after=after,
            direction=direction,
            page_size=page_size,
            page_token=page_token,
        )

    async def get_account_activities_by_activity_type(
        self,
        activity_type: ActivityType,
        date: Optional[datetime] = None,
        until: Optional[datetime] = None,
        after: Optional[datetime] = None,
        direction: Optional[SortDirection] = SortDirection.DESC,
        page_size: Optional[int] = 100,
        page_token: Optional[str] = None,
    ) -> Optional[AccountActivities]:
        """
        Retrieves account activities filtered by activity type from the Alpaca API.

        Args:
            activity_type (ActivityType): The activity type to filter results.
            date (Optional[datetime]): Specific date for filtering activities.
            until (Optional[datetime]): Filter activities before this date.
            after (Optional[datetime]): Filter activities after this date.
            direction (Optional[SortDirection]): 'asc' or 'desc', default is 'desc'.
            page_size (Optional[int]): Number of results to return per page, default is 100.
            page_token (Optional[str]): Token for pagination.

        Returns:
            Optional[AccountActivities]: A list of account activity objects filtered by the activity type.
        """
        return await self.account_client.get_account_activities_by_activity_type(
            activity_type=activity_type,
            date=date,
            until=until,
            after=after,
            direction=direction,
            page_size=page_size,
            page_token=page_token,
        )
