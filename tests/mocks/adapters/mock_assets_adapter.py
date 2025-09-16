from algo_royale.adapters.trading.assets_adapter import AssetsAdapter
from tests.mocks.clients.mock_alpaca_asset_client import MockAlpacaAssetsClient
from tests.mocks.mock_loggable import MockLoggable


class MockAssetsAdapter(AssetsAdapter):
    def __init__(self):
        assets_client = MockAlpacaAssetsClient()
        logger = MockLoggable()
        super().__init__(assets_client=assets_client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value
        self.assets_client.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False
        self.assets_client.return_empty = False
