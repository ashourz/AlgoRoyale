import asyncio

from algo_royale.backtester.pipeline.walk_forward_coordinator import (
    WalkForwardCoordinator,
)


async def async_cli(coordinator: WalkForwardCoordinator):
    """Async command line interface entry point"""
    success = await coordinator.run_async()
    exit(0 if success else 1)


def cli():
    """Synchronous CLI wrapper"""
    from algo_royale.di.container import (
        di_container,  # Import here to avoid circular dependency
    )

    coordinator = di_container.walk_forward_coordinator()
    asyncio.run(async_cli(coordinator))


if __name__ == "__main__":
    cli()
