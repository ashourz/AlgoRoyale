from algo_royale.clients.alpaca.exceptions import AlpacaAssetNotFoundException
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaAssetsClient:
    def __init__(self):
        self.logger = MockLoggable()

    async def fetch_assets(self):
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
        if symbol_or_asset_id == "AAPL":
            return (await self.fetch_assets())[0]
        raise AlpacaAssetNotFoundException()

    async def aclose(self):
        pass
