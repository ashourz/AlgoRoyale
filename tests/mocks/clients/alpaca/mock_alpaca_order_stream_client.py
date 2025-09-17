import asyncio
import json

from algo_royale.clients.alpaca.alpaca_trading.alpaca_order_stream_client import (
    AlpacaOrderStreamClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockWebSocket:
    def __init__(self, messages=None):
        self.sent = []
        self.closed = False
        # Simulate a sequence of messages to be received
        self._messages = messages or []
        self._recv_idx = 0

    async def send(self, msg):
        self.sent.append(msg)

    async def recv(self):
        # Simulate authentication and listen responses first
        if self._recv_idx < len(self._messages):
            msg = self._messages[self._recv_idx]
            self._recv_idx += 1
            return msg
        await asyncio.sleep(0.01)
        # Simulate a trade_updates message
        return json.dumps(
            {"stream": "trade_updates", "data": {"id": "order1", "status": "filled"}}
        )

    async def close(self):
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


class MockAlpacaOrderStreamClient(AlpacaOrderStreamClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="wss://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        self.return_empty = False
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    async def stream(self, on_order_update=None):
        if self.raise_exception:
            raise ValueError("WebSocket error")
        if self.return_empty:
            self.logger.info("Mock order stream returning empty, exiting.")
            return
        # Simulate the websocket handshake and a trade_updates message
        auth_response = json.dumps(
            {"stream": "authorization", "data": {"status": "authorized"}}
        )
        listen_response = json.dumps(
            {"stream": "listening", "data": {"streams": ["trade_updates"]}}
        )
        ws = MockWebSocket(messages=[auth_response, listen_response])
        self.websocket = ws
        self.logger.info("Mock order WebSocket connection established")
        # Simulate receiving a trade_updates message
        if on_order_update and not self.return_empty:
            msg = await ws.recv()
            # skip auth
            msg = await ws.recv()
            # skip listen
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("stream") == "trade_updates":
                await on_order_update(data["data"])
        await ws.close()
        self.logger.info("Mock order stream stopped.")
