from algo_royale.adapters.market_data.stream_adapter import StreamAdapter
from tests.mocks.clients.mock_alpaca_stream_client import MockAlpacaStreamClient
from tests.mocks.mock_loggable import MockLoggable


class MockStreamAdapter(StreamAdapter):
    def __init__(self):
        client = MockAlpacaStreamClient()
        logger = MockLoggable()
        super().__init__(stream_client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_stream(self, *args, **kwargs):
        if self.return_empty:
            return []
        return ["stream_event_1", "stream_event_2"]
