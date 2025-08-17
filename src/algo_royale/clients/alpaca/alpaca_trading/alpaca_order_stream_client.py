import asyncio
import json
from typing import Callable, Optional

from websockets.client import connect
from websockets.exceptions import ConnectionClosed

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig


class AlpacaOrderStreamClient(AlpacaBaseClient):
    """
    Singleton client for streaming real-time order updates from Alpaca WebSocket API.
    """

    def __init__(self, trading_config: TradingConfig):
        super().__init__(trading_config)
        self.trading_config = trading_config
        self.websocket = None
        self.stop_stream = False

    @property
    def client_name(self) -> str:
        return "AlpacaOrderStreamClient"

    @property
    def base_url(self) -> str:
        return self.trading_config.alpaca_params["base_url_trade_updates_stream"]

    async def stream(
        self,
        on_order_update: Optional[Callable] = None,
    ):
        """
        Start the stream for order updates.

        Args:
            on_order_update (callable): Coroutine function for trade_updates messages.
        """
        url = f"{self.base_url}"

        while not self.stop_stream:
            try:
                async with connect(url, ping_interval=self.keep_alive_timeout) as ws:
                    self.websocket = ws
                    await self._authenticate(ws)
                    await self._listen_trade_updates(ws)

                    self.logger.info("Order WebSocket connection established")

                    await self._receive_loop(ws, on_order_update)

            except Exception as e:
                self.logger.warning(f"Order WebSocket disconnected: {e}")
                self.logger.info(
                    f"Attempting reconnect in {self.reconnect_delay} seconds..."
                )
                await asyncio.sleep(self.reconnect_delay)

    async def _authenticate(self, ws):
        auth_msg = {"action": "auth", "key": self.api_key, "secret": self.api_secret}
        await ws.send(json.dumps(auth_msg))
        response = await ws.recv()
        self.logger.info(f"Auth response: {response}")

    async def _listen_trade_updates(self, ws):
        listen_msg = {"action": "listen", "data": {"streams": ["trade_updates"]}}
        await ws.send(json.dumps(listen_msg))
        response = await ws.recv()
        self.logger.info(f"Listen response: {response}")

    async def _receive_loop(self, ws, on_order_update):
        try:
            while not self.stop_stream:
                message = await ws.recv()
                data = json.loads(message)
                self.logger.debug(f"Received: {data}")

                if data.get("stream") == "trade_updates" and on_order_update:
                    await on_order_update(data["data"])
        except ConnectionClosed as e:
            self.logger.warning(f"Order WebSocket closed: {e}")
        except Exception as e:
            self.logger.error(f"Order receive error: {e}")

    async def stop(self):
        self.logger.info("Stopping order stream...")
        self.stop_stream = True
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.logger.info("Order stream stopped.")
        else:
            self.logger.warning("No active order stream to stop.")
