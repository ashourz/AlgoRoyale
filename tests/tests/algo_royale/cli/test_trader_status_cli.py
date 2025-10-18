import importlib
import os

import types
import sys


def _status_lock_path_for_env(env: str, status_module) -> str:
    return os.path.join(os.path.dirname(status_module.__file__), f"trader_{env}.lock")


def test_status_cli_reports_running(tmp_path, monkeypatch):
    """When the lock file exists, status CLI should return 0."""
    # Provide a minimal portalocker shim so importing single_instance_lock works
    fake_portalocker = types.SimpleNamespace()
    def _lock(handle, flags):
        return None
    def _unlock(handle):
        return None
    fake_portalocker.lock = _lock
    fake_portalocker.unlock = _unlock
    fake_portalocker.LOCK_EX = 1
    fake_portalocker.LOCK_NB = 2
    fake_portalocker.exceptions = types.SimpleNamespace(LockException=RuntimeError)
    monkeypatch.setitem(sys.modules, "portalocker", fake_portalocker)

    status_mod = importlib.import_module("algo_royale.cli.status_trader_dev_integration")
    lock_file = _status_lock_path_for_env("dev_integration", status_mod)

    # Ensure lock directory exists and create the lock file
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, "w") as fh:
        fh.write("12345")

    try:
        assert status_mod.cli("dev_integration") == 0
    finally:
        try:
            os.remove(lock_file)
        except Exception:
            pass


def test_status_cli_reports_not_running(monkeypatch):
    """When the lock file is absent, status CLI should return 1."""
    # Provide same portalocker shim for this test too
    fake_portalocker = types.SimpleNamespace()
    def _lock(handle, flags):
        return None
    def _unlock(handle):
        return None
    fake_portalocker.lock = _lock
    fake_portalocker.unlock = _unlock
    fake_portalocker.LOCK_EX = 1
    fake_portalocker.LOCK_NB = 2
    fake_portalocker.exceptions = types.SimpleNamespace(LockException=RuntimeError)
    monkeypatch.setitem(sys.modules, "portalocker", fake_portalocker)

    status_mod = importlib.import_module("algo_royale.cli.status_trader_dev_integration")
    lock_file = _status_lock_path_for_env("dev_integration", status_mod)

    # Ensure lock file is absent
    try:
        os.remove(lock_file)
    except Exception:
        pass

    assert status_mod.cli("dev_integration") == 1
