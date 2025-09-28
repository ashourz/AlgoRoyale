from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.symbol_hold_service import SymbolHoldService
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_order_event_service import MockOrderEventService
from tests.mocks.services.mock_order_service import MockOrderService
from tests.mocks.services.mock_positions_service import MockPositionsService
from tests.mocks.services.mock_symbol_hold_tracker import MockSymbolHoldTracker
from tests.mocks.services.mock_symbol_service import MockSymbolService
from tests.mocks.services.mock_trades_service import MockTradesService


class MockSymbolHoldService(SymbolHoldService):
    def __init__(self):
        super().__init__(
            symbol_service=MockSymbolService(),
            symbol_hold_tracker=MockSymbolHoldTracker(),
            order_service=MockOrderService(),
            order_event_service=MockOrderEventService(),
            positions_service=MockPositionsService(),
            trades_service=MockTradesService(),
            logger=MockLoggable(),
            post_fill_delay_seconds=0,
        )
        self.raise_exception = False
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.raise_exception = False
        self.return_empty = False

    async def start(self):
        if self.raise_exception:
            self.logger.error("Mocked exception on start")
        self.logger.info("MockSymbolHoldService started")

    async def stop(self):
        if self.raise_exception:
            self.logger.error("Mocked exception on stop")
        self.logger.info("MockSymbolHoldService stopped")

    async def async_subscribe_to_symbol_holds(self, callback):
        if self.raise_exception:
            self.logger.error("Mocked exception on async_subscribe_to_symbol_holds")
            return None
        if self.return_empty:
            return None
        return AsyncSubscriber(event_type="mock_event", callback=callback)

    def unsubscribe_from_symbol_holds(self, subscriber):
        self.logger.info("MockSymbolHoldService unsubscribed from symbol holds")

    async def async_subscribe_to_hold_roster(self, callback):
        if self.raise_exception:
            self.logger.error("Mocked exception on async_subscribe_to_hold_roster")
            return None
        if self.return_empty:
            return None
        return AsyncSubscriber(event_type="mock_event", callback=callback)

    def unsubscribe_from_hold_roster(self, subscriber):
        self.logger.info("MockSymbolHoldService unsubscribed from hold roster")
