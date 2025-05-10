## client\alpaca_trading\alpaca_calendar_client.py


from datetime import datetime
from typing import Optional
from algo_royale.live_trading.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.shared.models.alpaca_trading.alpaca_calendar import CalendarList
from algo_royale.shared.models.alpaca_trading.enums import CalendarDateType
from algo_royale.live_trading.config.config import ALPACA_TRADING_URL

class AlpacaCalendarClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCalendarClient"    

    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL
    
    async def fetch_calendar(
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
        
                
        response = await self.get(
            endpoint="calendar",
            params = params
        )   
        
        return CalendarList.from_raw(response)