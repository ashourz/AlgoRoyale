from typing import Callable

from pydantic import BaseModel

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.enums import DataFeed


class StreamSymbols(BaseModel):
    quotes: list[str]
    trades: list[str]
    bars: list[str]


class StreamAdapter:
    """
    Service class for managing Alpaca WebSocket streams and symbol subscriptions.

    This class serves as an abstraction layer to start, stop, and manage streaming operations
    for real-time stock market data from Alpaca. It simplifies integration and handling of events.
    """

    def __init__(self, stream_client: AlpacaStreamClient, logger: Loggable):
        """
        Initialize AlpacaStreamService with the provided AlpacaStreamClient.

        Args:
            stream_client (AlpacaStreamClient): Instance of AlpacaStreamClient for streaming data.
            logger (Loggable): Logger instance for logging events and errors.
        """
        self.stream_client = stream_client
        self.logger = logger

    def get_stream_symbols(self) -> StreamSymbols:
        """
        Get the currently subscribed stream symbols.

        Returns:
            StreamSymbols: An instance of StreamSymbols containing the subscribed symbols for quotes, trades, and bars.
        """
        return StreamSymbols(
            quotes=list(self.stream_client.quote_symbols),
            trades=list(self.stream_client.trade_symbols),
            bars=list(self.stream_client.bar_symbols),
        )

    async def async_start_stream(
        self,
        symbols: list[str],
        feed: DataFeed = DataFeed.IEX,
        on_quote: Callable = None,
        on_trade: Callable = None,
        on_bar: Callable = None,
    ):
        """
        Start streaming data for the provided symbols and feed.

        Args:
            symbols (list[str]): The list of symbols to subscribe to.
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

    async def async_add_symbols(
        self, quotes: list[str] = [], trades: list[str] = [], bars: list[str] = []
    ):
        """
        Add new symbols to the stream and subscribe to them.

        Args:
            quotes (list[str]): The list of symbols to subscribe to quote updates.
            trades (list[str]): The list of symbols to subscribe to trade updates.
            bars (list[str]): The list of symbols to subscribe to bar updates.
        """
        await self.stream_client.add_symbols(quotes=quotes, trades=trades, bars=bars)

    async def async_remove_symbols(
        self, quotes: list[str] = [], trades: list[str] = [], bars: list[str] = []
    ):
        """
        Remove symbols from the stream and unsubscribe from them.

        Args:
            quotes (list[str]): The list of symbols to unsubscribe from quote updates.
            trades (list[str]): The list of symbols to unsubscribe from trade updates.
            bars (list[str]): The list of symbols to unsubscribe from bar updates.
        """
        await self.stream_client.remove_symbols(quotes=quotes, trades=trades, bars=bars)

    async def async_stop_stream(self):
        """
        Stop the Alpaca WebSocket stream.
        """
        await self.stream_client.stop()
