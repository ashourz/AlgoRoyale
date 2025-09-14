# src: tests/integration/client/test_alpaca_account_client.py


from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import (
    AlpacaPositionsClient,
)
from algo_royale.clients.alpaca.exceptions import AlpacaPositionNotFoundException
from algo_royale.models.alpaca_trading.alpaca_position import (
    ClosedPosition,
    ClosedPositionList,
    Position,
    PositionList,
    PositionSide,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaPositionsClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    fake_position = Position(
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
    monkeypatch.setattr(
        client,
        "fetch_all_open_positions",
        AsyncMock(return_value=PositionList(positions=[fake_position])),
    )
    monkeypatch.setattr(
        client,
        "fetch_open_position_by_symbol_or_asset_id",
        AsyncMock(return_value=PositionList(positions=[fake_position])),
    )
    from algo_royale.models.alpaca_trading.alpaca_order import (
        Order,
        OrderSide,
        OrderType,
        TimeInForce,
    )
    from algo_royale.models.alpaca_trading.alpaca_position import (
        ClosedPosition,
        ClosedPositionList,
    )

    fake_order = Order(
        symbol="AAPL",
        qty=1,
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY,
        id="order_id",
        status="filled",
        client_order_id="client_order_id",
        created_at="2024-01-01T09:30:00",
        updated_at="2024-01-01T09:31:00",
        submitted_at="2024-01-01T09:30:00",
        asset_id="asset_id",
        asset_class="us_equity",
        filled_qty=1,
        order_type=OrderType.MARKET,
        extended_hours=False,
    )
    fake_closed_position = ClosedPosition(symbol="AAPL", status=200, order=fake_order)
    monkeypatch.setattr(
        client,
        "close_position_by_symbol_or_asset_id",
        AsyncMock(
            return_value=ClosedPositionList(closedPositions=[fake_closed_position])
        ),
    )
    monkeypatch.setattr(
        client,
        "close_all_positions",
        AsyncMock(
            return_value=ClosedPositionList(closedPositions=[fake_closed_position])
        ),
    )
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaPositionsClientIntegration:
    async def test_get_all_open_positions(self, alpaca_client):
        """Test fetching all open positions from Alpaca."""
        result = await alpaca_client.fetch_all_open_positions()

        assert result is not None
        assert isinstance(result, PositionList)
        assert isinstance(result.positions, list)

        for pos in result.positions:
            assert isinstance(pos, Position)
            assert isinstance(pos.asset_id, str)
            assert isinstance(pos.symbol, str)
            assert isinstance(pos.exchange, str)
            assert isinstance(pos.asset_class, str)
            assert isinstance(pos.asset_marginable, bool)
            assert isinstance(pos.qty, float)
            assert isinstance(pos.qty_available, float)
            assert isinstance(pos.avg_entry_price, float)
            assert isinstance(pos.side, PositionSide)
            assert pos.side in {PositionSide.long, PositionSide.short}
            assert isinstance(pos.market_value, float)
            assert isinstance(pos.cost_basis, float)
            assert isinstance(pos.unrealized_pl, float)
            assert isinstance(pos.unrealized_plpc, float)
            assert isinstance(pos.unrealized_intraday_pl, float)
            assert isinstance(pos.unrealized_intraday_plpc, float)
            assert isinstance(pos.current_price, float)
            assert isinstance(pos.lastday_price, float)
            assert isinstance(pos.change_today, float)

    async def test_get_open_position_by_symbol(self, alpaca_client):
        """Test fetching a single position by symbol."""
        symbol = "AAPL"  # Make sure this symbol has an open position
        try:
            result = await alpaca_client.fetch_open_position_by_symbol_or_asset_id(
                symbol
            )

            if result is not None:
                assert isinstance(result, PositionList)
                assert isinstance(result.positions, list)
                assert any(p.symbol == symbol for p in result.positions)
        except AlpacaPositionNotFoundException:
            pass

    async def test_close_position_by_symbol(self, alpaca_client):
        """Test closing a position by symbol with quantity."""
        symbol = "AAPL"  # Ensure you hold this position before running
        qty = 1
        try:
            result = await alpaca_client.close_position_by_symbol_or_asset_id(
                symbol_or_asset_id=symbol, qty=qty
            )

            if result is not None:
                assert isinstance(result, ClosedPositionList)
                assert hasattr(result, "closedPositions")
                assert isinstance(result.closedPositions, list)

                for closed in result.closedPositions:
                    assert isinstance(closed, ClosedPosition)
                    assert closed.symbol == symbol
                    assert closed.status == 200
                    assert closed.order is not None
        except AlpacaPositionNotFoundException:
            pass

    async def test_close_all_positions(self, alpaca_client):
        """Test closing all open positions."""
        result = await alpaca_client.close_all_positions()
        if result is not None:
            assert result is not None
            assert isinstance(result, ClosedPositionList)
            assert isinstance(result.closedPositions, list)

            for closed in result.closedPositions:
                assert isinstance(closed, ClosedPosition)
                assert isinstance(closed.symbol, str)
                assert closed.status == 200
                assert closed.order is not None
