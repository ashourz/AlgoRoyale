# src/algo_royale/service/alpaca_corporate_action_service.py

from datetime import datetime
from typing import List, Optional
from alpaca.common.enums import Sort

from algo_royale.the_risk_is_not_enough.client.alpaca_market_data.alpaca_corporate_action_client import AlpacaCorporateActionClient
from algo_royale.shared.models.alpaca_market_data.alpaca_corporate_action import CorporateActionResponse
from algo_royale.shared.models.alpaca_market_data.enums import CorporateActions


class AlpacaCorporateActionService:
    """
    Service class that wraps AlpacaCorporateActionClient to provide
    easier-to-use access to corporate actions, with additional business logic.
    """

    def __init__(self, client: Optional[AlpacaCorporateActionClient] = None):
        self.client = client or AlpacaCorporateActionClient()

    def get_corporate_actions_for_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        action_types: Optional[List[CorporateActions]] = None,
        sort_order: Sort = Sort.DESC,
        limit: int = 1000
    ) -> Optional[CorporateActionResponse]:
        """
        Fetch corporate actions for a list of stock symbols and a date range.
        """
        return self.client.fetch_corporate_actions(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            types=action_types or [],
            sort_order=sort_order,
            page_limit=limit
        )

    def get_corporate_actions_by_ids(
        self,
        action_ids: List[str],
        symbols: Optional[List[str]] = [],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[CorporateActionResponse]:
        """
        Fetch corporate actions using specific action IDs.
        Date range and symbols are optional filters.
        """
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.utcnow()

        return self.client.fetch_corporate_actions(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            ids=action_ids
        )
