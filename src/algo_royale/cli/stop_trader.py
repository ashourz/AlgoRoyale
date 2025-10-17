import argparse
import os

import json
import requests

from algo_royale.utils.single_instance_lock import stop_process

LOCK_FILE = os.path.join(os.path.dirname(__file__), "trader_prod_paper.lock")


def parse_args():
    """
    Parse command line arguments.

    Usage examples:
    ----------------
    # Run in dev_integration
    python stop_trader.py --env dev_integration

    # Run in prod_paper
    python stop_trader.py --env prod_paper

    # Run in prod_live
    python stop_trader.py --env prod_live
    """
    parser = argparse.ArgumentParser(description="Run the trading scheduler.")
    parser.add_argument(
        "--env",
        type=str,
        choices=["dev_integration", "prod_paper", "prod_live"],
        default="dev_integration",
        help="Select the environment to run the stop_trader in.",
    )
    return parser.parse_args()

def cli(lock_file: str):
    """Synchronous CLI wrapper"""
    # Try to read control.meta to discover control endpoint
    meta_file = os.path.join(os.path.dirname(__file__), '..', 'control.meta')
    if os.path.exists(meta_file):
        try:
            with open(meta_file) as f:
                meta = json.load(f)
            url = f"http://{meta.get('host')}:{meta.get('port')}/stop"
            # token header read from env
            headers = {}
            token = os.environ.get('ALGO_ROYALE_CONTROL_TOKEN')
            if token:
                headers['X-ALGO-TOKEN'] = token
            resp = requests.post(url, headers=headers, timeout=2)
            if resp.status_code in (200, 202):
                print('[Stop] Control endpoint accepted stop request.')
                return
        except Exception as e:
            print(f"[Stop] Control endpoint call failed: {e}. Falling back to PID kill.")

    stop_process(lock_file=lock_file)


def main():
    args = parse_args()
    lock_file = os.path.join(os.path.dirname(__file__), f"trader_{args.env}.lock")
    try:
        # Do NOT try to acquire the same lock the running process holds; doing so
        # will fail and prevent us from sending the stop signal. Instead, read
        # the PID from the lock file and signal it via stop_process.
        cli(lock_file)
    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C


if __name__ == "__main__":
    main()
