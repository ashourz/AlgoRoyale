import argparse
import os

from algo_royale.utils.single_instance_lock import status


def parse_args():
    """
    Parse command line arguments.

    Usage examples:
    ----------------
    # Run in dev_integration
    python status_trader.py --env dev_integration

    # Run in prod_paper
    python status_trader.py --env prod_paper

    # Run in prod_live without migrations
    python status_trader.py --env prod_live
    """
    parser = argparse.ArgumentParser(description="Check running status for a trader environment.")
    parser.add_argument(
        "--env",
        type=str,
        choices=["dev_integration", "prod_paper", "prod_live"],
        default="dev_integration",
        help="Select the environment to run the status trader in.",
    )

    return parser.parse_args()

def cli(env: str) -> int:
    """Check the running status for the given environment.

    Returns:
        0 if running (lock found), 1 if not running.
    """
    lock_file = os.path.join(os.path.dirname(__file__), f"trader_{env}.lock")
    status(lock_file)
    # `status` prints the result; return code is left for callers/tests
    pid_present = os.path.exists(lock_file)
    return 0 if pid_present else 1


def main():
    args = parse_args()
    try:
        code = cli(args.env)
        raise SystemExit(code)
    except KeyboardInterrupt:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
