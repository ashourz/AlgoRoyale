from unittest.mock import MagicMock

import pytest

from algo_royale.application.symbols.enums import SymbolHoldStatus
from src.algo_royale.application.symbols.symbol_hold_tracker import SymbolHoldTracker
from tests.mocks.mock_loggable import MockLoggable


@pytest.mark.asyncio
class TestSymbolHoldTracker:
    def setup_method(self):
        self.logger = MockLoggable()
        self.tracker = SymbolHoldTracker(self.logger)

    @pytest.mark.asyncio
    async def test_async_set_hold_and_pubsub(self):
        symbol = "AAPL"
        status = SymbolHoldStatus.HOLD_ALL
        await self.tracker.async_set_hold(symbol, status)
        assert self.tracker.symbol_holds[symbol] == status

    @pytest.mark.asyncio
    async def test_async_set_hold_exception(self):
        # Simulate exception by monkeypatching pubsub
        self.tracker._symbol_hold_pubsub.async_publish = MagicMock(
            side_effect=Exception("fail")
        )
        await self.tracker.async_set_hold("AAPL", SymbolHoldStatus.HOLD_ALL)
        # Should not raise, error is logged

    @pytest.mark.asyncio
    async def test_async_subscribe_to_symbol_holds_and_unsubscribe(self):
        async def callback(data):
            pass

        sub = await self.tracker.async_subscribe_to_symbol_holds(callback)
        assert sub is not None
        self.tracker.unsubscribe_from_symbol(sub)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_symbol_holds_exception(self):
        # Simulate exception in subscribe
        self.tracker._symbol_hold_pubsub.subscribe = MagicMock(
            side_effect=Exception("fail")
        )
        sub = await self.tracker.async_subscribe_to_symbol_holds(lambda x: x)
        assert sub is None

    @pytest.mark.asyncio
    async def test_async_subscribe_to_roster_and_unsubscribe(self):
        async def callback(data):
            pass

        sub = await self.tracker.async_subscribe_to_roster(callback)
        assert sub is not None
        await self.tracker.unsubscribe_from_roster(sub)

    @pytest.mark.asyncio
    async def test_async_subscribe_to_roster_exception(self):
        self.tracker._roster_hold_pubsub.subscribe = MagicMock(
            side_effect=Exception("fail")
        )
        sub = await self.tracker.async_subscribe_to_roster(lambda x: x)
        assert sub is None

    @pytest.mark.asyncio
    async def test_unsubscribe_from_symbol_exception(self):
        # Simulate exception in unsubscribe
        bad_sub = MagicMock()
        self.tracker._symbol_hold_pubsub.unsubscribe = MagicMock(
            side_effect=Exception("fail")
        )
        self.tracker.unsubscribe_from_symbol(bad_sub)

    @pytest.mark.asyncio
    async def test_unsubscribe_from_roster_exception(self):
        bad_sub = MagicMock()
        self.tracker._roster_hold_pubsub.unsubscribe = MagicMock(
            side_effect=Exception("fail")
        )
        await self.tracker.unsubscribe_from_roster(bad_sub)
