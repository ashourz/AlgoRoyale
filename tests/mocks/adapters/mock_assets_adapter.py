from algo_royale.adapters.trading.assets_adapter import AssetsAdapter
from tests.mocks.clients.mock_alpaca_asset_client import MockAlpacaAssetsClient
from tests.mocks.mock_loggable import MockLoggable


class MockAssetsAdapter(AssetsAdapter):
    def __init__(self):
        client = MockAlpacaAssetsClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False
