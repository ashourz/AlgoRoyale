from typing import Callable, List
from live_trading.client.alpaca_market_data.alpaca_stream_client import AlpacaStreamClient
from models.alpaca_market_data.enums import DataFeed


class AlpacaStreamService:
    """
    Service class for managing Alpaca WebSocket streams and symbol subscriptions.
    
    This class serves as an abstraction layer to start, stop, and manage streaming operations
    for real-time stock market data from Alpaca. It simplifies integration and handling of events.
    """

    def __init__(self, stream_client: AlpacaStreamClient):
        """
        Initialize AlpacaStreamService with the provided AlpacaStreamClient.
        
        Args:
            stream_client (AlpacaStreamClient): Instance of AlpacaStreamClient for streaming data.
        """
        self.stream_client = stream_client

    async def start_stream(
        self,
        symbols: List[str],
        feed: DataFeed = DataFeed.IEX,
        on_quote: Callable = None,
        on_trade: Callable = None,
        on_bar: Callable = None,
    ):
        """
        Start streaming data for the provided symbols and feed.

        Args:
            symbols (List[str]): The list of symbols to subscribe to.
            feed (DataFeed): The data feed to use (IEX, SIP, or TEST).
            on_quote (Callable): A coroutine function for handling quote messages.
            on_trade (Callable): A coroutine function for handling trade messages.
            on_bar (Callable): A coroutine function for handling bar messages.
        """
        await self.stream_client.stream(
            symbols=symbols,
            feed=feed,
            on_quote=on_quote,
            on_trade=on_trade,
            on_bar=on_bar,
        )

    async def add_symbols(self, quotes: List[str] = [], trades: List[str] = [], bars: List[str] = []):
        """
        Add new symbols to the stream and subscribe to them.

        Args:
            quotes (List[str]): The list of symbols to subscribe to quote updates.
            trades (List[str]): The list of symbols to subscribe to trade updates.
            bars (List[str]): The list of symbols to subscribe to bar updates.
        """
        await self.stream_client.add_symbols(quotes=quotes, trades=trades, bars=bars)

    async def remove_symbols(self, quotes: List[str] = [], trades: List[str] = [], bars: List[str] = []):
        """
        Remove symbols from the stream and unsubscribe from them.

        Args:
            quotes (List[str]): The list of symbols to unsubscribe from quote updates.
            trades (List[str]): The list of symbols to unsubscribe from trade updates.
            bars (List[str]): The list of symbols to unsubscribe from bar updates.
        """
        await self.stream_client.remove_symbols(quotes=quotes, trades=trades, bars=bars)

    def stop_stream(self):
        """
        Stop the Alpaca WebSocket stream.
        """
        self.stream_client.stop()
