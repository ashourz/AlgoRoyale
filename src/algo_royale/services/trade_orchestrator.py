from datetime import datetime, timedelta

from algo_royale.logging.loggable import Loggable
from algo_royale.services.clock_service import ClockService
from algo_royale.services.market_session_service import MarketSessionService


class TradeOrchestrator:
    def __init__(
        self,
        clock_service: ClockService,
        market_session_service: MarketSessionService,
        logger: Loggable,
        premarket_open_duration_minutes: int,
    ):
        self.clock_service = clock_service
        self.market_session_service = market_session_service
        self.logger = logger
        self.premarket_open_duration_minutes = premarket_open_duration_minutes
        self.pre_market_open_completed = False

    async def start(self):
        self.clock_service.start()
        await self.schedule_market_sessions()

    async def _on_pre_market_open(self):
        self.logger.info("Market pre-open")
        await self.market_session_service.async_start_premarket()

    async def _on_market_open(self):
        self.logger.info("Market opened")
        await self.market_session_service.async_start_market()

    async def _on_market_closed(self):
        self.logger.info("Market closed")
        await self.market_session_service.async_stop_market()
        # Start next market session
        self.logger.info("Scheduling next market sessions...")
        await self.schedule_market_sessions()

    async def stop(self):
        await self.clock_service.async_stop()

    async def schedule_market_sessions(self):
        """
        Schedule the market session tasks.
        """
        market_clock = await self.clock_service.async_get_market_clock()
        if not market_clock:
            self.logger.error(
                "Failed to retrieve market clock. Cannot schedule market sessions."
            )
            return
        market_open = self.clock_service.ensure_utc(market_clock.open)
        market_close = self.clock_service.ensure_utc(market_clock.close)
        if not market_open or not market_close:
            self.logger.error("Failed to retrieve market open/close times.")
            return
        if market_open and market_close:
            premarket_open = await self._get_premarket_open_utc(market_open)
            await self.clock_service.schedule_job(
                job_name="premarket_open",
                run_time=premarket_open,
                coro_func=self._on_pre_market_open,
            )
            await self.clock_service.schedule_job(
                job_name="market_open",
                run_time=market_open,
                coro_func=self._on_market_open,
            )
            await self.clock_service.schedule_job(
                job_name="market_close",
                run_time=market_close,
                coro_func=self._on_market_closed,
            )

    async def _get_premarket_open_utc(self, market_open_utc) -> datetime:
        """
        Calculate the pre-market open time in UTC.
        """
        premarket_open = market_open_utc - timedelta(
            minutes=self.premarket_open_duration_minutes
        )
        return premarket_open
