## client\alpaca_market_data\alpaca_corporate_action_client.py

from typing import List, Optional

from algo_royale.shared.models.alpaca_market_data.alpaca_corporate_action import CorporateActionResponse
from algo_royale.shared.models.alpaca_market_data.enums import CorporateActions
from algo_royale.live_trading.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.live_trading.config.config import ALPACA_PARAMS
from datetime import datetime
from alpaca.common.enums import Sort


class AlpacaCorporateActionClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for market data corporate action data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCorporateActionClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_PARAMS["base_url_data_v1"] 
        
    async def fetch_corporate_actions(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        cusips: List[str] = [],
        types: List[CorporateActions] = [],
        ids: List[str] = [],
        sort_order: Sort = Sort.DESC,
        page_limit: int = 1000,
        page_token: str = None,
    ) -> Optional[CorporateActionResponse]:
        """Fetch news data from Alpaca.
        
        attrs:
            symbols (list[str]): List of stock symbols to fetch news for.
            start_date (datetime): Start date for the news data.
            end_date (datetime): End date for the news data.
            cusips (list[str]): List of CUSIPs to filter by.
            types (list[CorporateActions]): List of corporate action types to filter by.
            ids (list[str]): List of IDs to filter by.
            sort_order (Sort): Sort order for the results. Default is descending.
            page_limit (int): Maximum number of results to return. Default is 1000.
            page_token (str): Token for pagination. Default is None.
        """

        if not isinstance(symbols, list):
            symbols = [symbols]
        if not isinstance(start_date, datetime):
            raise ValueError("start_date must be a datetime object")
        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")  
        
        params = {
            "symbols": ",".join(symbols),
            "start": start_date.strftime("%Y-%m-%d"),  # YYYY-MM-DD format
            "end": end_date.strftime("%Y-%m-%d"),      # YYYY-MM-DD format
            "sort": sort_order,
            "limit": min(page_limit, 1000),  # Alpaca limits to 1000
        }
        if cusips:
            params["cusips"] = cusips
        if types:
            params["types"] = types
        if ids:
            params["ids"] = ids
        if page_token is not None:
            params["page_token"] = page_token

        response = await self.get(
            endpoint="corporate-actions",
            params=params
        )
        
        return CorporateActionResponse.from_raw(response)