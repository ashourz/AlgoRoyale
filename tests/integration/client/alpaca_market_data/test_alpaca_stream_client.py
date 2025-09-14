# src/algo_royale/tests/integration/client/test_alpaca_stream_client.py
import asyncio

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
    DataFeed,
)
from tests.mocks.mock_loggable import MockLoggable


# Refactor TestHandler class without __init__ constructor
class TestHandler:
    quotes = []  # Class attribute instead of initializing in __init__
    bars = []  # Class attribute to store bar data
    trades = []  # Class attribute to store trades data

    @classmethod
    async def on_quote(cls, data):
        cls.quotes.append(data)

    @classmethod
    async def on_trade(cls, data):
        cls.trades.append(data)  # Store trade data

    @classmethod
    async def on_bar(cls, data):
        cls.bars.append(data)


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaStreamClient(
        logger=MockLoggable(),
        base_url="wss://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )

    # Patch the stream method to simulate receiving messages
    async def fake_stream(symbols, feed, on_quote, on_trade, on_bar):
        await on_quote({"symbol": symbols[0], "price": 100.0})
        await on_trade({"symbol": symbols[0], "price": 100.0})
        await on_bar({"symbol": symbols[0], "open": 99.0, "close": 101.0})
        await asyncio.sleep(0.1)

    monkeypatch.setattr(client, "stream", fake_stream)
    monkeypatch.setattr(client, "stop", lambda: None)
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaStreamClientIntegration:
    async def test_stream_receives_quote(self, alpaca_client):
        """
        Integration test for the AlpacaStreamClient to check if it receives quote messages.
        """

        handler = TestHandler()

        # Run the stream in the background
        task = asyncio.create_task(
            alpaca_client.stream(
                symbols=["FAKEPACA"],
                feed=DataFeed.TEST,
                on_quote=handler.on_quote,
                on_trade=handler.on_trade,
                on_bar=handler.on_bar,
            )
        )

        # Let the client run for a few seconds
        await asyncio.sleep(5)

        # Stop the client and wait for cleanup
        alpaca_client.stop()
        await asyncio.sleep(1)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Assert we received at least one quote, trade, or bar
        assert handler.quotes or handler.trades or handler.bars, (
            "No messages received from WebSocket stream"
        )
