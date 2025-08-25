import asyncio
from datetime import datetime, timezone
from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from algo_royale.adapters.trading.clock_adapter import ClockAdapter
from algo_royale.logging.loggable import Loggable


class ClockService:
    """Service class to interact with the clock adapter."""

    def __init__(self, clock_adapter: ClockAdapter, logger: Loggable):
        self.clock_adapter = clock_adapter
        self.scheduler = AsyncIOScheduler()
        self.stop_event = asyncio.Event()
        self.running_jobs = set()
        self.logger = logger

    def start(self):
        self.scheduler.start()

    async def stop(self):
        self.stop_event.set()
        self.scheduler.shutdown(wait=False)
        for task in list(self.running_jobs):
            task.cancel()
        await asyncio.gather(*self.running_jobs, return_exceptions=True)

    def schedule_job(
        self,
        job_name: str,
        coro_func: Callable[[], Awaitable[None]],
        run_time: datetime,
    ):
        async def wrapper():
            task = asyncio.current_task()
            self.running_jobs.add(task)
            try:
                self.logger.info(f"Starting scheduled job: {job_name}")
                await coro_func()
            except asyncio.CancelledError:
                self.logger.info(f"Scheduled job '{job_name}' was cancelled.")
            except Exception as e:
                self.logger.error(f"Error occurred in scheduled job '{job_name}': {e}")
            finally:
                self.logger.info(f"Finished scheduled job: {job_name}")
                self.running_jobs.discard(task)

        self.scheduler.add_job(
            func=wrapper, trigger="date", run_date=run_time, replace_existing=True
        )

    def get_system_time(self) -> datetime:
        """Get the current system time."""
        return datetime.now(timezone.utc)

    async def is_market_open(self) -> bool:
        """Check if the market is open."""
        try:
            market_clock = await self.clock_adapter.get_clock()
            if market_clock and market_clock.is_open:
                return True
        except Exception as e:
            self.logger.error(f"Error checking if market is open: {e}")
        return False

    async def is_market_closed(self) -> bool:
        """Check if the market is closed."""
        market_clock = await self.clock_adapter.get_clock()
        if market_clock and not market_clock.is_open:
            return True
        return False

    async def start_on_market_open(
        self,
        on_start: Callable[[], Awaitable[None]],
        on_stop: Callable[[], Awaitable[None]],
    ):
        """Start a task when the market opens and schedule the corresponding close.

        If the market is already open, `on_start` is executed immediately.
        Otherwise, it is scheduled at the next market open time (UTC).
        The market close (`on_stop`) is always scheduled at the next close time (UTC).
        """
        market_clock = await self.clock_adapter.get_clock()
        if market_clock is None:
            self.logger.warning("Market clock is not available.")
            return

        next_open_utc = self.ensure_utc(market_clock.next_open)
        next_close_utc = self.ensure_utc(market_clock.next_close)

        if market_clock.is_open:
            # Market already open → run immediately
            self.logger.info("Market is open. Running start task immediately.")
            current_time = self.get_system_time()
            self.schedule_job(
                job_name=f"market_open | {current_time.isoformat()}",
                coro_func=on_start,
                run_time=current_time,
            )
        elif next_open_utc:
            # Schedule start at next open
            self.logger.info(
                f"Scheduling next market open: {next_open_utc.isoformat()}"
            )
            self.schedule_job(
                job_name=f"market_open | {next_open_utc.isoformat()}",
                coro_func=on_start,
                run_time=next_open_utc,
            )
        else:
            self.logger.warning(
                "Next market open time is not available. Skipping start task."
            )

        if next_close_utc:
            # Always schedule stop at next close
            self.logger.info(
                f"Scheduling next market close: {next_close_utc.isoformat()}"
            )
            self.schedule_job(
                job_name=f"market_close | {next_close_utc.isoformat()}",
                coro_func=on_stop,
                run_time=next_close_utc,
            )
        else:
            self.logger.warning(
                "Next market close time is not available. Skipping stop task."
            )

    def ensure_utc(self, dt: datetime) -> datetime | None:
        """
        Ensure a datetime is timezone-aware and in UTC.

        - If naive, assume it is in local time and convert to UTC.
        - If tz-aware but not UTC, convert to UTC.
        - If already UTC, return as-is.
        """
        if dt.tzinfo is None:
            return None
        elif dt.tzinfo != timezone.utc:
            # Convert tz-aware datetime to UTC
            return dt.astimezone(timezone.utc)
        else:
            # Already UTC
            return dt
