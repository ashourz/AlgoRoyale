import asyncio

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
)
from algo_royale.models.alpaca_market_data.enums import DataFeed
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaStreamClient(AlpacaStreamClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="wss://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            data_stream_feed=DataFeed.TEST.value,
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        # Track symbol subscriptions for quotes, trades, bars
        self.quote_symbols = set()
        self.trade_symbols = set()
        self.bar_symbols = set()

    async def stream(self, symbols, on_quote, on_trade, on_bar):
        # Simulate subscribing to symbols for each type
        if on_quote is not None:
            self.quote_symbols.update(symbols)
            await on_quote({"symbol": symbols[0], "price": 100.0})
        if on_trade is not None:
            self.trade_symbols.update(symbols)
            await on_trade({"symbol": symbols[0], "price": 100.0})
        if on_bar is not None:
            self.bar_symbols.update(symbols)
            await on_bar({"symbol": symbols[0], "open": 99.0, "close": 101.0})
        await asyncio.sleep(0.1)

    def subscribe_quotes(self, symbols):
        self.quote_symbols.update(symbols)

    def subscribe_trades(self, symbols):
        self.trade_symbols.update(symbols)

    def subscribe_bars(self, symbols):
        self.bar_symbols.update(symbols)

    def unsubscribe_quotes(self, symbols):
        self.quote_symbols.difference_update(symbols)

    def unsubscribe_trades(self, symbols):
        self.trade_symbols.difference_update(symbols)

    def unsubscribe_bars(self, symbols):
        self.bar_symbols.difference_update(symbols)

    async def stop(self):
        pass
