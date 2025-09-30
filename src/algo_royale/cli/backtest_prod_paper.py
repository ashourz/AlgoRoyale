import asyncio
import os

from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.utils.single_instance_lock import SingleInstanceLock

LOCK_FILE = os.path.join(os.path.dirname(__file__), "backtest_prod_paper.lock")


async def async_cli(coordinator: PipelineCoordinator):
    """Async command line interface entry point"""
    success = await coordinator.run_async()
    exit(0 if success else 1)


def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.application_container import ApplicationContainer

    application_container = ApplicationContainer(environment=ApplicationEnv.PROD_PAPER)
    try:
        # Initialize and run DB migrations
        db_container = application_container.repo_container.db_container
        db_container.setup_environment()

        coordinator = (
            application_container.backtest_pipeline_container.pipeline_coordinator
        )
        asyncio.run(async_cli(coordinator))
    finally:
        if hasattr(application_container, "async_close"):
            asyncio.run(application_container.async_close())


def main():
    with SingleInstanceLock(LOCK_FILE):
        try:
            cli()
        except KeyboardInterrupt:
            pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
