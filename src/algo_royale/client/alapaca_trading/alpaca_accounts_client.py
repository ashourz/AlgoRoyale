# src/algo_royale/client/alpaca_news_client.py

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.client.exceptions import ParameterConflictError
from models.alpaca_trading.alpaca_account import Account, AccountActivities, AccountConfiguration
from models.alpaca_trading.enums import ActivityType, DTBPCheck, MarginMultiplier, OptionsTradingLevel, PDTCheck, SortDirection, TradeConfirmationEmail
from config.config import ALPACA_TRADING_URL

class AlpacaAccountClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaNewsClient"    
    
    def fetch_account(self) -> Optional[Account]:
        """Fetch account data from Alpaca."""

        responseJson = self._get(
            url=f"{self.base_url}/account"
        ).json()

        # self._logger.debug(f"News for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No account data available")
            return None       
        
        return Account.from_raw(responseJson)

    def fetch_account_configuration(self) -> Optional[AccountConfiguration]:
        """Fetch account data from Alpaca."""

        responseJson = self._get(
            url=f"{self.base_url}/account/configurations"
        ).json()

        # self._logger.debug(f"News for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No account data available")
            return None       
        
        return AccountConfiguration.from_raw(responseJson)

    def update_account_configuration(
        self,
        dtbp_check: Optional[DTBPCheck] = None,
        trade_confirm_email: Optional[TradeConfirmationEmail] = None,
        suspend_trade: Optional[bool] = None,
        no_shorting: Optional[bool] = None,
        fractional_trading: Optional[bool] = None,
        max_margin_multiplier: Optional[MarginMultiplier] = None,
        max_options_trading_level: Optional[OptionsTradingLevel] = None,
        pdt_check: Optional[PDTCheck] = None,
        ptp_no_exception_entry: Optional[bool] = None
    ) -> Optional[AccountConfiguration]:
        """
        Update and fetch account configuration from Alpaca.

        Args are all optional, used to update account configuration settings.
        """
        payload = {}

        if dtbp_check is not None:
            payload["dtbp_check"] = dtbp_check.value if isinstance(dtbp_check, Enum) else dtbp_check
        if trade_confirm_email is not None:
            payload["trade_confirm_email"] = trade_confirm_email.value if isinstance(trade_confirm_email, Enum) else trade_confirm_email
        if suspend_trade is not None:
            payload["suspend_trade"] = suspend_trade
        if no_shorting is not None:
            payload["no_shorting"] = no_shorting
        if fractional_trading is not None:
            payload["fractional_trading"] = fractional_trading
        if max_margin_multiplier is not None:
            payload["max_margin_multiplier"] = max_margin_multiplier
        if max_options_trading_level is not None:
            payload["max_options_trading_level"] = max_options_trading_level
        if pdt_check is not None:
            payload["pdt_check"] = pdt_check
        if ptp_no_exception_entry is not None:
            payload["ptp_no_exception_entry"] = ptp_no_exception_entry

        # Send the PATCH request
        response = self._patch(
            url=f"{self.base_url}/account/configurations",
            payload=payload
        )

        if response.status_code != 200:
            self._logger.warning(f"Failed to update account config: {response.status_code} {response.text}")
            return None

        response_json = response.json()
        return AccountConfiguration.from_raw(response_json)

    def get_account_activities(
        self,
        activity_types: Optional[List[ActivityType]] = None,
        category: Optional[str] = None,
        date: Optional[datetime] = None,
        until: Optional[datetime] = None,
        after: Optional[datetime] = None,
        direction: Optional[SortDirection] = SortDirection.DESC,
        page_size: Optional[int] = 100,
        page_token: Optional[str] = None
    ) -> Optional[AccountActivities]:
        """
        Retrieve account activities from Alpaca API.

        Args:
            activity_types (Optional[List[ActivityType]]): List of activity types to filter results.
            category (Optional[str]): Activity category (mutually exclusive with activity_types).
            date (Optional[datetime]): Specific date for filtering.
            until (Optional[datetime]): Filter for activities before this date.
            after (Optional[datetime]): Filter for activities after this date.
            direction (Optional[SortDirection]): 'asc' or 'desc', default is 'desc'.
            page_size (Optional[int]): Number of results to return per page, default is 100.
            page_token (Optional[str]): Token for pagination.

        Returns:
            Optional[AccountActivities]: A list of account activity objects.
        """
        
        if activity_types and category:
            raise ParameterConflictError("Specify either 'activity_types' or 'category' or neither, not both.")
        
        params = {}

        if activity_types:
            # Convert ActivityType enum values to their string representation for the API call
            params["activity_types"] = ",".join([activity_type.value for activity_type in activity_types])
        if category:
            params["category"] = category
        if date:
            params["date"] = date
        if until:
            params["until"] = until
        if after:
            params["after"] = after
        if direction:
            params["direction"] = direction
        if page_size:
            params["page_size"] = str(page_size)
        if page_token:
            params["page_token"] = page_token

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response = self._get(
            url=f"{self.base_url}/account/activities",
            params=params
        )

        if response.status_code != 200:
            self._logger.warning(f"Failed to retrieve account activities: {response.status_code} {response.text}")
            return None

        response_json = response.json()
        return AccountActivities.from_raw(response_json)
    
    def get_account_activities_by_activity_type(
        self,
        activity_type: ActivityType,
        date: Optional[datetime] = None,
        until: Optional[datetime] = None,
        after: Optional[datetime] = None,
        direction: Optional[SortDirection] = SortDirection.DESC,
        page_size: Optional[int] = 100,
        page_token: Optional[str] = None
    ) -> Optional[AccountActivities]:
        """
        Retrieve account activities from Alpaca API.

        Args:
            activity_type (ActivityType): Activity type to filter results.
            date (Optional[datetime]): Specific date for filtering.
            until (Optional[datetime]): Filter for activities before this date.
            after (Optional[datetime]): Filter for activities after this date.
            direction (Optional[str]): 'asc' or 'desc', default is 'desc'.
            page_size (Optional[int]): Number of results to return per page, default is 100.
            page_token (Optional[str]): Token for pagination.

        Returns:
            Optional[AccountActivities]: A list of account activity objects.
        """
        
        params = {}

        if date:
            params["date"] = date.isoformat()
        if until:
            params["until"] = until.isoformat()
        if after:
            params["after"] = after.isoformat()
        if direction:
            params["direction"] = direction
        if page_size:
            params["page_size"] = str(page_size)
        if page_token:
            params["page_token"] = page_token

        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        response = self._get(
            url=f"{self.base_url}/account/activities/{activity_type.value}",
            params=params
        )

        if response.status_code != 200:
            self._logger.warning(f"Failed to retrieve account activities: {response.status_code} {response.text}")
            return None

        response_json = response.json()
        return AccountActivities.from_raw(response_json)