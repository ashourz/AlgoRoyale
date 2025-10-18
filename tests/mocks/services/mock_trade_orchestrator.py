from algo_royale.services.trade_orchestrator import TradeOrchestrator
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService
from tests.mocks.services.mock_market_session_service import MockMarketSessionService


class MockTradeOrchestrator(TradeOrchestrator):
    def __init__(self):
        super().__init__(
            clock_service=MockClockService(),
            market_session_service=MockMarketSessionService(),
            premarket_open_duration_minutes=15,
            logger=MockLoggable(),
        )
        self.started = False
        self.stopped = False

    def async_start(self):
        self.started = True
        return super().async_start()
    
    async def async_stop(self):
        self.stopped = True
        return await super().async_stop()
