from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.symbol_hold_tracker import SymbolHoldTracker
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from tests.mocks.mock_loggable import MockLoggable


class MockSymbolHoldTracker(SymbolHoldTracker):
    def __init__(self):
        super().__init__(
            logger=MockLoggable(),
        )
        self.symbol_holds = {}
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def reset(self):
        self.symbol_holds = {}
        self.return_empty = False

    async def async_set_hold(self, symbol: str, status: SymbolHoldStatus):
        # Mock implementation: just log the action
        self.logger.info(f"Mock set hold for {symbol} to {status}")
        self.symbol_holds[symbol] = status

    async def async_subscribe_to_symbol_holds(
        self,
        callback,
        queue_size: int = -1,
    ):
        # Mock implementation: return a dummy AsyncSubscriber
        self.logger.info("Mock subscribe to symbol holds")
        if self.return_empty:
            return None
        return AsyncSubscriber(event_type="mock_event", callback=callback)

    def unsubscribe_from_symbol(self, async_subscriber: AsyncSubscriber):
        # Mock implementation: just log the action
        self.logger.info("Mock unsubscribe from symbol holds")

    async def async_subscribe_to_roster(self, callback):
        # Mock implementation: return a dummy AsyncSubscriber
        self.logger.info("Mock subscribe to roster")
        if self.return_empty:
            return None
        return AsyncSubscriber(event_type="mock_event", callback=callback)

    def unsubscribe_from_roster(self, async_subscriber: AsyncSubscriber):
        # Mock implementation: just log the action
        self.logger.info("Mock unsubscribe from roster")
