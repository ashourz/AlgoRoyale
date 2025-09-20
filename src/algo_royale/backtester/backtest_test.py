import asyncio

from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.logging.logger_env import LoggerEnv


async def async_cli(coordinator: PipelineCoordinator):
    """Async command line interface entry point"""
    success = await coordinator.run_async()
    exit(0 if success else 1)


def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.application_container import ApplicationContainer

    application_container = ApplicationContainer(environment=LoggerEnv.TEST)
    coordinator = (
        application_container.backtest_pipeline_container().pipeline_coordinator()
    )
    asyncio.run(async_cli(coordinator))


if __name__ == "__main__":
    cli()
