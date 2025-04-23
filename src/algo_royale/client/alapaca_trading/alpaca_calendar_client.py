# src/algo_royale/client/alpaca_corporate_action_client.py


from datetime import datetime
from typing import Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_market_data.alpaca_corporate_action import CorporateActionDateType
from models.alpaca_trading.alpaca_calendar import CalendarList
from models.alpaca_trading.enums import CalendarDateType
from config.config import ALPACA_TRADING_URL

class AlpacaCalendarClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCalendarClient"    
    
    def fetch_calendar(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        date_type: Optional[CalendarDateType] = None
    ) -> Optional[CalendarList]:
        """Fetch calendar data from Alpaca."""

        params = {}

        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if date_type:
            params["date_type"] = date_type
        
        # Format all non-None parameters
        for k, v in params.items():
            if v is not None:
                params[k] = self._format_param(v)
                
        responseJson = self._get(
            url=f"{self.base_url}/calendar",
            params = params
        ).json()

        if responseJson is None:
            self._logger.warning(f"No calendar data available")
            return None       
        
        return CalendarList.from_raw(responseJson)