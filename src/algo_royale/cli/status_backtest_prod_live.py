import os

from algo_royale.utils.single_instance_lock import status

LOCK_FILE = os.path.join(os.path.dirname(__file__), "backtest_prod_live.lock")


def cli():
    """Synchronous CLI wrapper"""
    status(LOCK_FILE)


def main():
    try:
        cli()
    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
