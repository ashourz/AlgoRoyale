import copy
import uuid
from datetime import datetime

from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.models.alpaca_trading.alpaca_asset import Asset
from algo_royale.models.alpaca_trading.alpaca_watchlist import Watchlist
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaWatchlistClient(AlpacaWatchlistClient):
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
        self._watchlists_by_id = {}
        self._watchlists_by_name = {}
        self.return_empty = False

    def _make_watchlist(self, name, symbols=None, wid=None):
        assets = []
        if symbols:
            for symbol in symbols:
                assets.append(
                    Asset(
                        id=f"asset_{symbol}",
                        class_="us_equity",
                        exchange="NASDAQ",
                        symbol=symbol,
                        name=symbol,
                        status="active",
                        tradable=True,
                        marginable=True,
                        shortable=True,
                        easy_to_borrow=True,
                        fractionable=True,
                        maintenance_margin_requirement=30,
                        attributes=[],
                    )
                )
        return Watchlist(
            id=wid or f"watchlist_{uuid.uuid4().hex[:8]}",
            account_id="account_id",
            created_at=datetime(2024, 1, 1, 9, 30, 0),
            updated_at=datetime(2024, 1, 1, 9, 31, 0),
            name=name,
            assets=assets,
        )

    async def create_watchlist(self, name, symbols=None):
        wl = self._make_watchlist(name, symbols)
        self._watchlists_by_id[wl.id] = wl
        self._watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl)

    async def get_watchlist_by_name(self, name):
        wl = self._watchlists_by_name.get(name)
        return copy.deepcopy(wl) if wl else None

    async def get_watchlist_by_id(self, wid):
        wl = self._watchlists_by_id.get(wid)
        return copy.deepcopy(wl) if wl else None

    async def get_all_watchlists(self):
        class Resp:
            watchlists = [copy.deepcopy(wl) for wl in self._watchlists_by_id.values()]

        return Resp()

    async def update_watchlist_by_id(self, watchlist_id, name=None, **kwargs):
        wl = self._watchlists_by_id.get(watchlist_id)
        if wl and name:
            del self._watchlists_by_name[wl.name]
            wl.name = name
            self._watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl) if wl else None

    async def update_watchlist_by_name(self, name, update_name=None, **kwargs):
        wl = self._watchlists_by_name.get(name)
        if wl and update_name:
            del self._watchlists_by_name[wl.name]
            wl.name = update_name
            self._watchlists_by_name[wl.name] = wl
        return copy.deepcopy(wl) if wl else None

    async def add_asset_to_watchlist_by_id(self, watchlist_id, symbol):
        wl = self._watchlists_by_id.get(watchlist_id)
        if wl and not any(a.symbol == symbol for a in wl.assets):
            wl.assets.append(
                Asset(
                    id=f"asset_{symbol}",
                    class_="us_equity",
                    exchange="NASDAQ",
                    symbol=symbol,
                    name=symbol,
                    status="active",
                    tradable=True,
                    marginable=True,
                    shortable=True,
                    easy_to_borrow=True,
                    fractionable=True,
                    maintenance_margin_requirement=30,
                    attributes=[],
                )
            )
        return copy.deepcopy(wl) if wl else None

    async def add_asset_to_watchlist_by_name(self, name, symbol):
        wl = self._watchlists_by_name.get(name)
        if wl and not any(a.symbol == symbol for a in wl.assets):
            wl.assets.append(
                Asset(
                    id=f"asset_{symbol}",
                    class_="us_equity",
                    exchange="NASDAQ",
                    symbol=symbol,
                    name=symbol,
                    status="active",
                    tradable=True,
                    marginable=True,
                    shortable=True,
                    easy_to_borrow=True,
                    fractionable=True,
                    maintenance_margin_requirement=30,
                    attributes=[],
                )
            )
        return copy.deepcopy(wl) if wl else None

    async def delete_symbol_from_watchlist(self, watchlist_id, symbol):
        wl = self._watchlists_by_id.get(watchlist_id)
        if wl:
            wl.assets = [a for a in wl.assets if a.symbol != symbol]
        return copy.deepcopy(wl) if wl else None

    async def delete_watchlist_by_id(self, watchlist_id):
        wl = self._watchlists_by_id.pop(watchlist_id, None)
        if wl:
            self._watchlists_by_name.pop(wl.name, None)
        return True

    async def delete_watchlist_by_name(self, name):
        wl = self._watchlists_by_name.pop(name, None)
        if wl:
            self._watchlists_by_id.pop(wl.id, None)
        return True
