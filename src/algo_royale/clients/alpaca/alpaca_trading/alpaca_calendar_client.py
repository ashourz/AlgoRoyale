## client\alpaca_trading\alpaca_calendar_client.py


from datetime import datetime
from typing import Optional
from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig
from algo_royale.models.alpaca_trading.alpaca_calendar import CalendarList
from algo_royale.models.alpaca_trading.enums import CalendarDateType

class AlpacaCalendarClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 

    def __init__(self, trading_config: TradingConfig):
        """Initialize the AlpacaStockClient with trading configuration."""
        super().__init__(trading_config)
        self.trading_config = trading_config
        
    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaCalendarClient"    

    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return self.trading_config.get_base_url()
    
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