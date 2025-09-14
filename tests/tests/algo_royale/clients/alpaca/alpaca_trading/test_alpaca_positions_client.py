# src: tests/integration/client/test_alpaca_account_client.py


import pytest

from algo_royale.clients.alpaca.exceptions import AlpacaPositionNotFoundException
from algo_royale.models.alpaca_trading.alpaca_position import (
    ClosedPosition,
    ClosedPositionList,
    Position,
    PositionList,
    PositionSide,
)
from tests.mocks.clients.mock_alpaca_positions_client import MockAlpacaPositionsClient


@pytest.fixture
async def alpaca_client():
    client = MockAlpacaPositionsClient()
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
