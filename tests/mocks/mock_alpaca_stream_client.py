import asyncio

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
)


class MockAlpacaStreamClient(AlpacaStreamClient):
    def __init__(self, logger):
        super().__init__(
            logger=logger,
            base_url="wss://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )

    async def stream(self, symbols, feed, on_quote, on_trade, on_bar):
        await on_quote({"symbol": symbols[0], "price": 100.0})
        await on_trade({"symbol": symbols[0], "price": 100.0})
        await on_bar({"symbol": symbols[0], "open": 99.0, "close": 101.0})
        await asyncio.sleep(0.1)

    def stop(self):
        pass
