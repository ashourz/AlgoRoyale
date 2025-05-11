## client\alpaca_trading\alpaca_clock_client.py


from typing import Optional
from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig
from algo_royale.models.alpaca_trading.alpaca_clock import Clock

class AlpacaClockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 

    def __init__(self, trading_config: TradingConfig):
        """Initialize the AlpacaStockClient with trading configuration."""
        super().__init__(trading_config)
        self.trading_config = trading_config
        
    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaClockClient"    

    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return self.trading_config.get_base_url()
    
    async def fetch_clock(self) -> Optional[Clock]:
        """Fetch clock data from Alpaca."""

        response = await self.get(
            endpoint="/clock"
        )    
        
        return Clock.from_raw(response)