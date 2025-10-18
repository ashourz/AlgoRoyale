# src/algo_royale/tests/integration/client/test_alpaca_stream_client.py
import asyncio

from algo_royale.models.alpaca_market_data.enums import DataFeed
import pytest

from tests.mocks.clients.alpaca.mock_alpaca_stream_client import MockAlpacaStreamClient


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
async def alpaca_client():
    client = MockAlpacaStreamClient()
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
