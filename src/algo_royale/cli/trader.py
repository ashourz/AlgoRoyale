import asyncio
import os
import argparse

from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.services.trade_orchestrator import TradeOrchestrator
from algo_royale.utils.single_instance_lock import SingleInstanceLock
from algo_royale.utils.control_server import ControlServer


def parse_args():
    """
    Parse command line arguments.

    Usage examples:
    ----------------
    # Run in dev_integration without forcing migrations
    python trader.py --env dev_integration

    # Run in prod_paper and force migrations
    python trader.py --env prod_paper --run-migrations

    # Run in prod_live without migrations
    python trader.py --env prod_live
    """
    parser = argparse.ArgumentParser(description="Run the trading scheduler.")
    parser.add_argument(
        "--env",
        type=str,
        choices=["dev_integration", "prod_paper", "prod_live"],
        default="dev_integration",
        help="Select the environment to run the scheduler in.",
    )
    parser.add_argument(
        "--run-migrations",
        action="store_true",
        help="Force running pending DB migrations before starting scheduler.",
    )
    return parser.parse_args()


async def async_cli(orchestrator: TradeOrchestrator, control_token: str):
    """
    Async scheduler entry point.

    This runs your trading-day scheduler asynchronously and keeps it alive
    until the end of the trading day or until cancelled (Ctrl+C or system stop).

    Usage:
    ------
    Called internally by the main CLI after environment is prepared.
    """
    # start orchestrator
    success = await orchestrator.async_start()
    control = ControlServer(token=control_token)
    control.set_stop_callback(orchestrator.async_stop)
    # start control server in background
    await control.start()
    print(f"Control server listening on {control.host}:{control.port}")
    try:
        while True:
            # Keep scheduler alive for trading day
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        await orchestrator.async_stop()
    finally:
        await control.stop()
    exit(0 if success else 1)


def cli(env: str, run_migrations: bool):
    """
    Synchronous CLI wrapper.

    Responsibilities:
    -----------------
    1. Initializes the application container for the specified environment.
    2. Applies pending migrations if the DB is uninitialized or --run-migrations is passed.
    3. Starts the async trading scheduler.

    Parameters:
    ----------
    env: str - One of ["dev_integration", "prod_paper", "prod_live"]
    run_migrations: bool - Whether to force running migrations
    """
    from algo_royale.di.application_container import ApplicationContainer

    # Map string to ApplicationEnv
    env_map = {
        "dev_integration": ApplicationEnv.DEV_INTEGRATION,
        "prod_paper": ApplicationEnv.PROD_PAPER,
        "prod_live": ApplicationEnv.PROD_LIVE,
    }
    application_env = env_map[env]

    # Load secrets for the given environment into process env before constructing container
    from algo_royale.utils.secrets_loader import load_env_secrets
    load_env_secrets(env)

    application_container = ApplicationContainer(environment=application_env)
    try:
        db_container = application_container.repo_container.db_container

        # Run migrations automatically if requested or if DB is uninitialized
        if run_migrations or not db_container.is_initialized():
            print(f"🔄 Running migrations for {env}...")
            db_container.setup_environment()
            print(f"✅ Migrations applied for {env}")

        orchestrator: TradeOrchestrator = application_container.trading_container.trade_orchestrator
        from algo_royale.utils.secrets_loader import get_control_token
        token = get_control_token(env)
        if token is None:
            print("Error: Control token not found. Cannot start control server.")
            exit(1)
        asyncio.run(async_cli(orchestrator, control_token=token))
    finally:
        if hasattr(application_container, "async_close"):
            asyncio.run(application_container.async_close())


def main():
    """
    Main entry point for the CLI.

    Features:
    ---------
    - Parses CLI arguments
    - Uses SingleInstanceLock to prevent multiple schedulers for the same env
    - Calls the main CLI function
    """
    args = parse_args()
    lock_file = os.path.join(
        os.path.dirname(__file__), f"trader_{args.env}.lock"
    )

    with SingleInstanceLock(lock_file):
        try:
            cli(env=args.env, run_migrations=args.run_migrations)
        except KeyboardInterrupt:
            pass  # Graceful exit on Ctrl+C

if __name__ == "__main__":
    main()

def run_dev():
    """Run trader in dev_integration without migrations"""
    cli(env="dev_integration", run_migrations=True)

def run_paper():
    """Run trader in prod_paper and force migrations"""
    cli(env="prod_paper", run_migrations=True)

def run_live():
    """Run trader in prod_live without migrations"""
    cli(env="prod_live", run_migrations=True)