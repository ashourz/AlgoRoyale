import argparse
import asyncio
import os

from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.utils.single_instance_lock import SingleInstanceLock

LOCK_FILE = os.path.join(os.path.dirname(__file__), "drop_prod_live.lock")


def cli(username: str):
    """Synchronous CLI wrapper"""
    from algo_royale.di.application_container import ApplicationContainer

    application_container = ApplicationContainer(environment=ApplicationEnv.PROD_LIVE)
    try:
        # Initialize and run DB migrations
        db_container = application_container.repo_container.db_container
        db_container.drop_user(username=username)
    finally:
        if hasattr(application_container, "async_close"):
            asyncio.run(application_container.async_close())


def main():
    parser = argparse.ArgumentParser(
        description="Drop a user from the prod live database."
    )
    parser.add_argument("username", type=str, help="The username to drop.")
    args = parser.parse_args()
    with SingleInstanceLock(LOCK_FILE):
        try:
            cli(username=args.username)
        except KeyboardInterrupt:
            pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
