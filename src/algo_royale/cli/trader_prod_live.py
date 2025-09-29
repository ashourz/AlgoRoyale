import asyncio
import os

from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.services.trade_orchestrator import TradeOrchestrator
from algo_royale.utils.single_instance_lock import SingleInstanceLock

LOCK_FILE = os.path.join(os.path.dirname(__file__), "trader_prod_paper.lock")
lock = SingleInstanceLock(LOCK_FILE)
lock.acquire()


async def async_cli(orchestrator: TradeOrchestrator):
    """Async command line interface entry point"""
    success = await orchestrator.async_start()
    exit(0 if success else 1)


def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.application_container import ApplicationContainer

    application_container = ApplicationContainer(environment=ApplicationEnv.PROD_LIVE)
    try:
        # Initialize and run DB migrations
        db_container = application_container.repo_container().db_container()
        db_container.run_migrations()

        orchestrator = application_container.trading_container().trade_orchestrator()
        asyncio.run(async_cli(orchestrator))
    finally:
        if hasattr(application_container, "async_close"):
            asyncio.run(application_container.async_close())


if __name__ == "__main__":
    try:
        cli()
    finally:
        lock.release()
