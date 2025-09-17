import copy

from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import (
    AlpacaPositionsClient,
)
from algo_royale.clients.alpaca.exceptions import AlpacaPositionNotFoundException
from algo_royale.models.alpaca_trading.alpaca_order import (
    Order,
    OrderSide,
    OrderType,
    TimeInForce,
)
from algo_royale.models.alpaca_trading.alpaca_position import (
    ClosedPosition,
    ClosedPositionList,
    Position,
    PositionList,
    PositionSide,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaPositionsClient(AlpacaPositionsClient):
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
        self.raise_exception = False
        self._positions = {}
        self._closed_positions = []
        # Add a default open position
        pos = Position(
            asset_id="asset_id",
            symbol="AAPL",
            exchange="NASDAQ",
            asset_class="us_equity",
            asset_marginable=True,
            qty=10.0,
            qty_available=10.0,
            avg_entry_price=150.0,
            side=PositionSide.long,
            market_value=1500.0,
            cost_basis=1500.0,
            unrealized_pl=0.0,
            unrealized_plpc=0.0,
            unrealized_intraday_pl=0.0,
            unrealized_intraday_plpc=0.0,
            current_price=150.0,
            lastday_price=149.0,
            change_today=0.01,
        )
        self._positions[pos.symbol] = pos

    async def fetch_all_open_positions(self):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaPositionsClient: Exception forced by raise_exception flag."
            )
        if self.return_empty:
            return PositionList(positions=[])
        return PositionList(
            positions=[copy.deepcopy(p) for p in self._positions.values()]
        )

    async def fetch_open_position_by_symbol_or_asset_id(self, symbol_or_id):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaPositionsClient: Exception forced by raise_exception flag."
            )
        if self.return_empty:
            return PositionList(positions=[])
        pos = self._positions.get(symbol_or_id)
        if pos:
            return PositionList(positions=[copy.deepcopy(pos)])
        raise AlpacaPositionNotFoundException()

    async def close_position_by_symbol_or_asset_id(
        self, symbol_or_asset_id, qty=None, percentage=None, **kwargs
    ):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaPositionsClient: Exception forced by raise_exception flag."
            )
        if self.return_empty:
            return ClosedPositionList(closedPositions=[])
        pos = self._positions.get(symbol_or_asset_id)
        if pos:
            # Optionally handle qty (simulate partial close if needed)
            if qty is not None and qty < pos.qty:
                pos.qty -= qty
                pos.qty_available -= qty
                closed_qty = qty
            else:
                closed_qty = pos.qty
                self._positions.pop(symbol_or_asset_id)
            fake_order = Order(
                symbol=pos.symbol,
                qty=closed_qty,
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY,
                id="order_id",
                status="filled",
                client_order_id="client_order_id",
                created_at="2024-01-01T09:30:00",
                updated_at="2024-01-01T09:31:00",
                submitted_at="2024-01-01T09:30:00",
                asset_id=pos.asset_id,
                asset_class=pos.asset_class,
                filled_qty=closed_qty,
                order_type=OrderType.MARKET,
                extended_hours=False,
            )
            closed = ClosedPosition(symbol=pos.symbol, status=200, order=fake_order)
            self._closed_positions.append(closed)
            return ClosedPositionList(closedPositions=[copy.deepcopy(closed)])
        raise AlpacaPositionNotFoundException()

    async def close_all_positions(self, cancel_orders=None, **kwargs):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaPositionsClient: Exception forced by raise_exception flag."
            )
        if self.return_empty:
            return ClosedPositionList(closedPositions=[])
        closed = []
        for symbol in list(self._positions.keys()):
            closed += (
                await self.close_position_by_symbol_or_asset_id(symbol)
            ).closedPositions
        return ClosedPositionList(closedPositions=closed)
