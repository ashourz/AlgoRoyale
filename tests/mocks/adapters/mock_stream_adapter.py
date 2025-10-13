from algo_royale.adapters.market_data.stream_adapter import StreamAdapter
from tests.mocks.clients.alpaca.mock_alpaca_stream_client import MockAlpacaStreamClient
from tests.mocks.mock_loggable import MockLoggable


class MockAsyncSubscriber:
    pass


class MockStreamDataIngestObject:
    def subscribe(self, callback, queue_size=1):
        return MockAsyncSubscriber()

    def unsubscribe(self, subscriber):
        pass


class MockStreamAdapter(StreamAdapter):
    def __init__(self):
        client = MockAlpacaStreamClient()
        logger = MockLoggable()
        super().__init__(stream_client=client, logger=logger)
        self.return_empty = False
        self.stream_data_ingest_object_map = {}
        self.stream_subscribers = {}

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.return_empty = False
        self.stream_data_ingest_object_map = {}
        self.stream_subscribers = {}

    async def async_subscribe_to_stream(self, symbols, callback):
        if self.return_empty:
            return {}
        result = {}
        for symbol in symbols:
            ingest_obj = self.stream_data_ingest_object_map.setdefault(
                symbol, MockStreamDataIngestObject()
            )
            subscriber = ingest_obj.subscribe(callback)
            self.stream_subscribers.setdefault(symbol, []).append(subscriber)
            result[symbol] = subscriber
        return result

    async def async_unsubscribe_from_stream(self, symbol_subscribers):
        for symbol, subscribers in symbol_subscribers.items():
            if symbol in self.stream_subscribers:
                for subscriber in subscribers:
                    try:
                        self.stream_subscribers[symbol].remove(subscriber)
                    except ValueError:
                        pass
                if not self.stream_subscribers[symbol]:
                    del self.stream_subscribers[symbol]
