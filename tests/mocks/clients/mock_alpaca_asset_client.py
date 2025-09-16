from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import (
    AlpacaAssetsClient,
)
from algo_royale.clients.alpaca.exceptions import AlpacaAssetNotFoundException
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaAssetsClient(AlpacaAssetsClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        self.return_empty = False
        self.throw_exception = False

    async def fetch_assets(self, status=None, asset_class="us_equity", exchange=None):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAssetsClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return []
        fake_asset = Asset(
            id="asset_id",
            class_="us_equity",
            exchange="NASDAQ",
            symbol="AAPL",
            name="Apple Inc.",
            status="active",
            tradable=True,
            marginable=True,
            maintenance_margin_requirement=25,
            shortable=True,
            easy_to_borrow=True,
            fractionable=True,
            attributes=[],
        )
        return [fake_asset]

    async def fetch_asset_by_symbol_or_id(self, symbol_or_asset_id):
        if self.throw_exception:
            raise AlpacaAssetNotFoundException()
        if self.return_empty:
            return None
        if symbol_or_asset_id == "AAPL":
            assets = await self.fetch_assets()
            if not assets:
                return None
            return assets[0]
        raise AlpacaAssetNotFoundException()

    async def aclose(self):
        pass
