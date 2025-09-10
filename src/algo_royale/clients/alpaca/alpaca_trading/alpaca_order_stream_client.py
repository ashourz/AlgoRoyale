import asyncio
import json
from typing import Callable, Optional

from websockets.client import connect
from websockets.exceptions import ConnectionClosed

from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.logging.loggable import Loggable


class AlpacaOrderStreamClient(AlpacaBaseClient):
    """
    Singleton client for streaming real-time order updates from Alpaca WebSocket API.
    """

    def __init__(
        self,
        logger: Loggable,
        base_url: str,
        api_key: str,
        api_secret: str,
        api_key_header: str,
        api_secret_header: str,
        http_timeout: int = 10,
        reconnect_delay: int = 5,
        keep_alive_timeout: int = 20,
    ):
        super().__init__(
            logger=logger,
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret,
            api_key_header=api_key_header,
            api_secret_header=api_secret_header,
            http_timeout=http_timeout,
            reconnect_delay=reconnect_delay,
            keep_alive_timeout=keep_alive_timeout,
        )
        self.websocket = None
        self.stop_stream = False

    @property
    def client_name(self) -> str:
        return "AlpacaOrderStreamClient"

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
