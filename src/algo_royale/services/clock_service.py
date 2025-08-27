import asyncio
from datetime import datetime, timezone
from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from algo_royale.adapters.trading.clock_adapter import ClockAdapter
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_clock import Clock


class ClockService:
    """Service class to interact with the clock adapter."""

    def __init__(
        self,
        clock_adapter: ClockAdapter,
        logger: Loggable,
    ):
        self.clock_adapter = clock_adapter
        self.scheduler = AsyncIOScheduler()
        self.stop_event = asyncio.Event()
        self.running_jobs = set()
        self.logger = logger

    def start(self):
        self.scheduler.start()

    async def async_stop(self):
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
        """
        Schedule a job to run at a specific time.
        If the job is due to run within the next 60 seconds, execute it immediately.
        Otherwise, schedule it to run at the specified time.
        """
        now = self.get_system_utc_time()
        duration_until_start = (run_time - now).total_seconds()
        if duration_until_start < 60:
            self.logger.warning(
                f"Scheduled job '{job_name}' is approaching. It will be executed immediately."
            )
            task = asyncio.create_task(coro_func())
            self.running_jobs.add(task)
            return
        else:

            async def wrapper():
                task = asyncio.current_task()
                self.running_jobs.add(task)
                try:
                    self.logger.info(f"Starting scheduled job: {job_name}")
                    await coro_func()
                except asyncio.CancelledError:
                    self.logger.info(f"Scheduled job '{job_name}' was cancelled.")
                except Exception as e:
                    self.logger.error(
                        f"Error occurred in scheduled job '{job_name}': {e}"
                    )
                finally:
                    self.logger.info(f"Finished scheduled job: {job_name}")
                    self.running_jobs.discard(task)

            self.scheduler.add_job(
                name=job_name,
                func=wrapper,
                trigger="date",
                run_date=run_time,
                replace_existing=True,
            )

    def get_system_utc_time(self) -> datetime:
        """Get the current system time."""
        return datetime.now(timezone.utc)

    async def async_get_market_clock(self) -> Clock | None:
        """Get the market clock."""
        market_clock = await self.clock_adapter.get_clock()
        return market_clock if market_clock else None

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
