# src/algo_royale/client/alpaca_stream_client.py
import asyncio
import json
import websockets
from enum import Enum
import logging

from config.config import ALPACA_PARAMS

class DataFeed(Enum):
    IEX = "iex"
    SIP = "sip"
    TEST = "test"

class AlpacaStreamClient:
    _instance = None
    _lock = asyncio.Lock()
    """
    Singleton client for streaming real-time stock market data (quotes, trades, bars) from Alpaca WebSocket API.
    
    Features:
    - Reconnection handling
    - Keep-alive pings
    - Dynamic symbol subscriptions/unsubscriptions
    - Asynchronous event handling
    """

    def __init__(self):
        """
        Initialize the stream client.

        Args:
            api_key (str): Alpaca API key.
            api_secret (str): Alpaca API secret.
            base_url_data_stream (str): Base URL for Alpaca WebSocket stream.
        """
        self.api_key = ALPACA_PARAMS["api_key"]
        self.api_secret = ALPACA_PARAMS["api_secret"]
        self.base_url_data_stream = ALPACA_PARAMS["base_url_data_stream"]
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG) 

        self.websocket = None
        self.stop_stream = False

        # Sets to track what you're subscribed to
        self.quote_symbols = set()
        self.trade_symbols = set()
        self.bar_symbols = set()

        # Configurable reconnect delay and keep-alive timeout
        self.reconnect_delay = ALPACA_PARAMS.get("reconnect_delay", 5)
        self.keep_alive_timeout = ALPACA_PARAMS.get("keep_alive_timeout", 20)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlpacaStreamClient, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    async def stream(
        self,
        symbols: list[str],
        feed: DataFeed = DataFeed.IEX,
        on_quote: callable = None,
        on_trade: callable = None,
        on_bar: callable = None,
    ):
        """
        Start the stream for given symbols and handlers.

        Args:
            symbols (list[str]): Initial list of symbols to subscribe to.
            feed (DataFeed): Chosen feed type (IEX or SIP).
                - IEX: IEX Cloud data (free tier).
                - SIP: SIP data (paid tier).
                - TEST: Test data (for development purposes).
            on_quote (callable): Coroutine function for quote messages. 
                - Occurs: Every time the best bid or ask price for a stock changes.
            on_trade (callable): Coroutine function for trade messages.
                - Occurs: Every time a buy and sell order are matched and a trade is executed.
            on_bar (callable): Coroutine function for bar messages.
                - Occurs: At regular intervals (e.g., every minute) to summarize price movements.
        """
        self.quote_symbols.update(symbols)

        url = f"{self.base_url_data_stream}/{feed.value}"

        while not self.stop_stream:
            try:
                async with websockets.connect(url, ping_interval=self.keep_alive_timeout) as ws:
                    self.websocket = ws
                    await self._authenticate(ws)
                    await self._send_subscription(ws)

                    self.logger.info("WebSocket connection established")

                    # Run both loops concurrently
                    await asyncio.gather(
                        self._receive_loop(ws, on_quote, on_trade, on_bar),
                        self._ping_loop(ws)
                    )

            except Exception as e:
                self.logger.warning(f"WebSocket disconnected: {e}")
                self.logger.info(f"Attempting reconnect in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)

    async def _authenticate(self, ws):
        """Authenticate with the WebSocket using API key/secret."""
        auth_msg = {
            "action": "auth",
            "key": self.api_key,
            "secret": self.api_secret
        }
        await ws.send(json.dumps(auth_msg))
        response = await ws.recv()
        self.logger.info(f"Auth response: {response}")

    async def _send_subscription(self, ws):
        """Send subscription message for quotes/trades/bars."""
        msg = {
            "action": "subscribe",
            "quotes": list(self.quote_symbols),
            "trades": list(self.trade_symbols),
            "bars": list(self.bar_symbols)
        }
        await ws.send(json.dumps(msg))
        self.logger.info(f"Subscribed to quotes: {self.quote_symbols}, trades: {self.trade_symbols}, bars: {self.bar_symbols}")

    async def _unsubscribe(self, ws, quotes=[], trades=[], bars=[]):
        """Send unsubscribe message."""
        msg = {
            "action": "unsubscribe",
            "quotes": quotes,
            "trades": trades,
            "bars": bars
        }
        await ws.send(json.dumps(msg))
        self.logger.info(f"Unsubscribed from quotes: {quotes}, trades: {trades}, bars: {bars}")

    async def _receive_loop(self, ws, on_quote, on_trade, on_bar):
        """
        Continuously receive and handle incoming messages.

        Args:
            ws: WebSocket connection.
            on_quote: Callable to handle quote messages.
            on_trade: Callable to handle trade messages.
            on_bar: Callable to handle bar messages.
        """
        try:
            while not self.stop_stream:
                message = await ws.recv()
                data = json.loads(message)
                self.logger.debug(f"Received: {data}")

                # Handle each item in list individually
                for item in data if isinstance(data, list) else [data]:
                    msg_type = item.get("T")
                    if msg_type == "q" and on_quote: # Quote message
                        await on_quote(item)
                    elif msg_type == "t" and on_trade: # Trade message
                        await on_trade(item)
                    elif msg_type == "b" and on_bar: # Bar message
                        await on_bar(item)

        except websockets.ConnectionClosed as e:
            self.logger.warning(f"WebSocket closed: {e}")
        except Exception as e:
            self.logger.error(f"Receive error: {e}")

    async def _ping_loop(self, ws):
        """Send periodic ping messages to keep the connection alive."""
        try:
            while not self.stop_stream:
                ping_msg = {"action": "ping"}
                await ws.send(json.dumps(ping_msg))
                self.logger.debug("Sent ping")
                await asyncio.sleep(self.keep_alive_timeout)
        except Exception as e:
            self.logger.warning(f"Ping loop terminated: {e}")

    async def add_symbols(self, quotes=[], trades=[], bars=[]):
        """
        Add new symbols dynamically and subscribe to them.

        Args:
            quotes (list[str]): Symbols for quote updates.
            trades (list[str]): Symbols for trade updates.
            bars (list[str]): Symbols for bar updates.
        """
        if self.websocket and self.websocket.open:
            await self._send_subscription(self.websocket)

        self.quote_symbols.update(quotes)
        self.trade_symbols.update(trades)
        self.bar_symbols.update(bars)

    async def remove_symbols(self, quotes=[], trades=[], bars=[]):
        """
        Remove symbols dynamically and unsubscribe from them.

        Args:
            quotes (list[str]): Symbols to unsubscribe from quote updates.
            trades (list[str]): Symbols to unsubscribe from trade updates.
            bars (list[str]): Symbols to unsubscribe from bar updates.
        """
        if self.websocket and self.websocket.open:
            await self._unsubscribe(self.websocket, quotes, trades, bars)

        self.quote_symbols.difference_update(quotes)
        self.trade_symbols.difference_update(trades)
        self.bar_symbols.difference_update(bars)

    def stop(self):
        """
        Stop the WebSocket stream gracefully.
        """
        self.logger.info("Stopping stream...")
        self.stop_stream = True
