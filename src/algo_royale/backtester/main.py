import asyncio
from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
import pandas as pd


async def async_cli(coordinator: PipelineCoordinator):
    """Async command line interface entry point"""
    success = await coordinator.run_async()
    exit(0 if success else 1)

def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.container import di_container  # Import here to avoid circular dependency
    coordinator = di_container.pipeline_coordinator() 
    asyncio.run(async_cli(coordinator))

if __name__ == "__main__":
    cli()