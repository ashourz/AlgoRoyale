# src/algo_royale/client/alpaca_corporate_action_client.py

from enum import Enum
from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_models.alpaca_corporate_action import CorporateActionResponse
from datetime import datetime
from alpaca.common.enums import Sort
from config.config import ALPACA_PARAMS

class CorporateActions(Enum):
    """
    Enum for different types of corporate actions.
    These can be used to categorize or filter corporate actions when fetching data.

    Types:   
    - REVERSE_SPLIT: Represents a reverse stock split.
    - FORWARD_SPLIT: Represents a forward stock split.
    - UNIT_SPLIT: Represents a unit stock split.
    - CASH_DIVIDEND: Represents a cash dividend.
    - STOCK_DIVIDEND: Represents a stock dividend.
    - SPIN_OFF: Represents a spin-off of a company.
    - CASH_MERGER: Represents a cash merger.
    - STOCK_MERGER: Represents a stock merger.
    - STOCK_CASH_MERGER: Represents a stock and cash merger.
    - REDEMPTION: Represents a redemption of shares.
    - NAME_CHANGE: Represents a name change of a company.
    - WORTHLESS_REMOVAL: Represents the removal of worthless shares.
    - RIGHTS_DISTRIBUTION: Represents a rights distribution.
    """
    
    REVERSE_SPLIT = "reverse_split"
    FORWARD_SPLIT = "forward_split"
    UNIT_SPLIT = "unit_split"
    CASH_DIVIDEND = "cash_dividend"
    STOCK_DIVIDEND = "stock_dividend"
    SPIN_OFF = "spin_off"
    CASH_MERGER = "cash_merger"
    STOCK_MERGER = "stock_merger"
    STOCK_CASH_MERGER = "stock_and_cash_merger"
    REDEMPTION = "redemption"
    NAME_CHANGE = "name_change"
    WORTHLESS_REMOVAL = "worthless_removal"
    RIGHTS_DISTRIBUTION = "rights_distribution"

class AlpacaCorporateActionClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_PARAMS["base_url_data_v1"] 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCorporateActionClient"    
    
    def fetch_corporate_actions(
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
            params["cusips"] = ",".join(cusips)
        if types:
            params["types"] = ",".join(types)
        if ids:
            params["ids"] = ",".join(ids)
        if page_token is not None:
            params["page_token"] = page_token

            
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/corporate-actions",
            params=params
        )

        if responseJson is None:
            self._logger.warning(f"No corporate action data available for {symbols}")
            return None       
        
        return CorporateActionResponse.from_raw(responseJson)


            