# src/algo_royale/service/alpaca_corporate_action_service.py

from datetime import datetime
from typing import Optional

from alpaca.common.enums import Sort

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateActionResponse,
)
from algo_royale.models.alpaca_market_data.enums import CorporateActions
from algo_royale.utils.clock_provider import ClockProvider


class CorporateActionAdapter:
    """
    Service class that wraps AlpacaCorporateActionClient to provide
    easier-to-use access to corporate actions, with additional business logic.
    """

    def __init__(
        self,
        client: AlpacaCorporateActionClient,
        clock_provider: ClockProvider,
        logger: Loggable,
    ):
        """
        Initialize the CorporateActionAdapter with the AlpacaCorporateActionClient and a logger.

        Args:
            client (AlpacaCorporateActionClient): Instance of AlpacaCorporateActionClient for API calls.
            logger (Loggable): Logger instance for logging events and errors.
        """
        self.client = client
        self.clock_provider = clock_provider
        self.logger = logger

    async def get_corporate_actions_for_symbols(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        action_types: Optional[list[CorporateActions]] = None,
        sort_order: Sort = Sort.DESC,
        limit: int = 1000,
    ) -> Optional[CorporateActionResponse]:
        """
        Fetch corporate actions for a list of stock symbols and a date range.
        """
        return await self.client.fetch_corporate_actions(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            types=action_types or [],
            sort_order=sort_order,
            page_limit=limit,
        )

    async def get_corporate_actions_by_ids(
        self,
        action_ids: list[str],
        symbols: Optional[list[str]] = [],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[CorporateActionResponse]:
        """
        Fetch corporate actions using specific action IDs.
        Date range and symbols are optional filters.
        """
        if not start_date:
            start_date = self.clock_provider.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if not end_date:
            end_date = self.clock_provider.now()

        return await self.client.fetch_corporate_actions(
            symbols=symbols, start_date=start_date, end_date=end_date, ids=action_ids
        )
