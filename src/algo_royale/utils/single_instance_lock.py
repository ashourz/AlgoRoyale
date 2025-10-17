import os
import signal
import subprocess
import sys
import time
from typing import Optional

import portalocker


class SingleInstanceLock:
    """Cross-platform single-instance lock using portalocker.

    The lock file also contains the process PID so external tools can signal
    the process for graceful shutdown.
    """

    def __init__(self, lock_file: str):
        self.lock_file = lock_file
        self.handle = None

    def __enter__(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.lock_file), exist_ok=True)

        # Open file for locking
        self.handle = open(self.lock_file, "w+")

        try:
            # Acquire an exclusive non-blocking lock
            portalocker.lock(self.handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
        except portalocker.exceptions.LockException:
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
            try:
                portalocker.unlock(self.handle)
            except Exception:
                pass
            self.handle.close()
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                print(f"[Lock] Released lock and removed {self.lock_file}")
        except Exception as e:
            print(f"[Lock] Cleanup error: {e}")


def get_pid(lock_file: str) -> Optional[int]:
    """Returns the PID stored in the lock file, if it exists."""
    if not os.path.exists(lock_file):
        return None
    try:
        with open(lock_file) as f:
            return int(f.read().strip())
    except Exception:
        return None


def _kill_windows(pid: int):
    # Use taskkill to terminate process tree on Windows
    try:
        subprocess.check_call(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def stop_process(lock_file: str):
    """Gracefully stops the process associated with this lock file.

    On Unix: sends SIGINT to allow graceful shutdown. On Windows: uses taskkill.
    """
    pid = get_pid(lock_file)
    if not pid:
        print("[Stop] No running instance found.")
        return

    if sys.platform == "win32":
        print(f"[Stop] Windows detected. Using taskkill to terminate PID {pid}...")
        ok = _kill_windows(pid)
        if not ok:
            print("[Stop] Could not terminate process. It may not exist or permissions are insufficient.")
            # If process is gone, remove stale lock
            if get_pid(lock_file) is None:
                try:
                    os.remove(lock_file)
                except Exception:
                    pass
            return
    else:
        print(f"[Stop] Sending SIGINT to PID {pid}...")
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            print("[Stop] Process not found. Removing stale lock file.")
            try:
                os.remove(lock_file)
            except Exception:
                pass
            return

    # Wait for graceful shutdown (lock file removal)
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
