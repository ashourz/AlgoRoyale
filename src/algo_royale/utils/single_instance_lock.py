import fcntl
import os
import signal
import sys
import time


class SingleInstanceLock:
    """
    Prevents multiple instances of the same process from running.
    Also writes a PID file to allow graceful remote shutdown.
    """

    def __init__(self, lock_file: str):
        self.lock_file = lock_file
        self.handle = None

    def __enter__(self):
        # Open file for locking
        self.handle = open(self.lock_file, "w")

        try:
            # Acquire an exclusive non-blocking lock
            fcntl.lockf(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            print(f"[Lock] Another instance is already running ({self.lock_file}).")
            sys.exit(1)

        # Write the current process PID to file
        pid = str(os.getpid())
        self.handle.seek(0)
        self.handle.write(pid)
        self.handle.truncate()
        self.handle.flush()
        print(f"[Lock] Acquired lock. PID={pid}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.handle.close()
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                print(f"[Lock] Released lock and removed {self.lock_file}")
        except Exception as e:
            print(f"[Lock] Cleanup error: {e}")


def get_pid(lock_file: str) -> int | None:
    """Returns the PID stored in the lock file, if it exists."""
    if not os.path.exists(lock_file):
        return None
    try:
        with open(lock_file) as f:
            return int(f.read().strip())
    except Exception:
        return None


def stop_process(lock_file: str):
    """Gracefully stops the process associated with this lock file."""
    pid = get_pid(lock_file)
    if not pid:
        print("[Stop] No running instance found.")
        return

    print(f"[Stop] Sending SIGINT to PID {pid}...")
    try:
        os.kill(pid, signal.SIGINT)
    except ProcessLookupError:
        print("[Stop] Process not found. Removing stale lock file.")
        os.remove(lock_file)
        return

    # Optional: wait for graceful shutdown
    for _ in range(10):
        time.sleep(0.5)
        if not os.path.exists(lock_file):
            print("[Stop] Process stopped gracefully.")
            return
    print("[Stop] Process may still be shutting down...")


def status(lock_file: str):
    """Checks if the process is currently running."""
    pid = get_pid(lock_file)
    if not pid:
        print("[Status] Not running.")
        return
    print(f"[Status] Running with PID {pid}.")
