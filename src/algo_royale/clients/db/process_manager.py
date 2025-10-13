import os
import platform
import subprocess

import psutil

from algo_royale.logging.loggable import Loggable


class ProcessManager:
    _PID_FILE = "algo_royale_app.pids"

    def __init__(self, logger: Loggable):
        self.logger = logger
        if not os.path.exists(self._PID_FILE):
            with open(self._PID_FILE, "w") as f:
                f.write("")

    def register_instance(self):
        pid = os.getpid()
        try:
            with open(self._PID_FILE, "a") as f:
                f.write(f"{pid}\n")
        except Exception as e:
            self.logger.error(f"Error registering PID: {e}")

    def unregister_instance(self):
        pid = os.getpid()
        try:
            if not os.path.exists(self._PID_FILE):
                return
            with open(self._PID_FILE, "r") as f:
                pids = [line.strip() for line in f if line.strip()]
            pids = [p for p in pids if p != str(pid)]
            with open(self._PID_FILE, "w") as f:
                for p in pids:
                    f.write(f"{p}\n")
        except Exception as e:
            self.logger.error(f"Error unregistering PID: {e}")

    def any_other_instances_running(self):
        pid = os.getpid()
        if not os.path.exists(self._PID_FILE):
            return False
        try:
            with open(self._PID_FILE, "r") as f:
                pids = [
                    int(line.strip())
                    for line in f
                    if line.strip() and line.strip().isdigit()
                ]
            for p in pids:
                if p != pid and psutil.pid_exists(p):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking other instances: {e}")
            return False

    def is_postgres_running(self, host: str, port: int, timeout: float = 2.0) -> bool:
        import socket

        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, ConnectionRefusedError):
            return False

    def start_postgres_service(self, service_name: str = "postgresql-x64-13") -> bool:
        if platform.system() != "Windows":
            raise NotImplementedError(
                "start_postgres_service is only implemented for Windows."
            )
        try:
            query = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "RUNNING" in query.stdout:
                return True
            result = subprocess.run(
                ["sc", "start", service_name], capture_output=True, text=True
            )
            if (
                "START_PENDING" in result.stdout
                or "RUNNING" in result.stdout
                or result.returncode == 0
            ):
                return True
            if "already running" in result.stdout.lower():
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error starting PostgreSQL service: {e}")
            return False

    def stop_postgres_service(self, service_name: str = "postgresql-x64-13") -> bool:
        if platform.system() != "Windows":
            raise NotImplementedError(
                "stop_postgres_service is only implemented for Windows."
            )
        try:
            query = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "STOPPED" in query.stdout:
                return True
            result = subprocess.run(
                ["sc", "stop", service_name], capture_output=True, text=True
            )
            if (
                "STOP_PENDING" in result.stdout
                or "STOPPED" in result.stdout
                or result.returncode == 0
            ):
                return True
            if "already stopped" in result.stdout.lower():
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping PostgreSQL service: {e}")
            return False
