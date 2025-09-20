import os
import sys


class SingleInstanceLock:
    def __init__(self, lock_file):
        self.lock_file = lock_file

    def acquire(self):
        if os.path.exists(self.lock_file):
            print(
                f"Another instance is already running (lock file exists: {self.lock_file})"
            )
            sys.exit(1)
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))

    def release(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
