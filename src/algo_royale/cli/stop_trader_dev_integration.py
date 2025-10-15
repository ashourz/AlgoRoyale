import os

from algo_royale.utils.single_instance_lock import SingleInstanceLock, stop_process

LOCK_FILE = os.path.join(os.path.dirname(__file__), "trader_dev_integration.lock")


def cli():
    """Synchronous CLI wrapper"""

    stop_process(LOCK_FILE)


def main():
    with SingleInstanceLock(LOCK_FILE):
        try:
            cli()
        except KeyboardInterrupt:
            pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
