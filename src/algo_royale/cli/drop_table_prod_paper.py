import argparse
import asyncio
import os

from algo_royale.utils.application_env import ApplicationEnv
from algo_royale.utils.single_instance_lock import SingleInstanceLock

LOCK_FILE = os.path.join(os.path.dirname(__file__), "drop_prod_paper.lock")


def cli(db_name: str, table_name: str):
    """Synchronous CLI wrapper"""
    from algo_royale.di.application_container import ApplicationContainer

    application_container = ApplicationContainer(environment=ApplicationEnv.PROD_PAPER)
    try:
        # Initialize and run DB migrations
        db_container = application_container.repo_container.db_container
        db_container.drop_table(db_name=db_name, table_name=table_name)
    finally:
        if hasattr(application_container, "async_close"):
            asyncio.run(application_container.async_close())


def main():
    parser = argparse.ArgumentParser(
        description="Drop a table from the prod paper database."
    )
    parser.add_argument("db_name", type=str, help="The name of the database.")
    parser.add_argument("table_name", type=str, help="The name of the table to drop.")
    args = parser.parse_args()
    with SingleInstanceLock(LOCK_FILE):
        try:
            cli(db_name=args.db_name, table_name=args.table_name)
        except KeyboardInterrupt:
            pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
