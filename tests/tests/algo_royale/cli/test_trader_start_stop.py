import asyncio
import importlib
import json
import os

import pytest
import sys
import types
import builtins
from tests.mocks.services.mock_trade_orchestrator import MockTradeOrchestrator

# Top-level configuration: which modules to test. Change these if you want
# to point the same tests at different entrypoints.
START_CLI_MODULE = "algo_royale.cli.trader"
STOP_CLI_MODULE = "algo_royale.cli.stop_trader"


@pytest.fixture
def orchestrator():
    orchestrator = MockTradeOrchestrator()
    yield orchestrator
    
@pytest.mark.asyncio
async def test_async_cli_start_and_stop(monkeypatch, orchestrator: MockTradeOrchestrator):
    """Ensure async_cli starts orchestrator and control server, and cleans up on cancel."""

    # Provide a minimal portalocker shim so importing SingleInstanceLock works
    fake_portalocker = types.SimpleNamespace()

    def _lock(handle, flags):
        return None

    def _unlock(handle):
        return None

    class LockException(Exception):
        pass

    fake_portalocker.lock = _lock
    fake_portalocker.unlock = _unlock
    fake_portalocker.LOCK_EX = 1
    fake_portalocker.LOCK_NB = 2
    fake_portalocker.exceptions = types.SimpleNamespace(LockException=LockException)

    monkeypatch.setitem(sys.modules, "portalocker", fake_portalocker)

    # import the entrypoint module dynamically so tests can be re-pointed
    # by editing START_CLI_MODULE above

    trader_mod = importlib.import_module(START_CLI_MODULE)


    # Mock ControlServer to avoid binding sockets
    class MockControlServer:
        def __init__(self, token, host='127.0.0.1', port=8765):
            self.token = token
            self.host = host
            self.port = port
            self.started = False
            self.stopped = False
            self._stop_cb = None

        def set_stop_callback(self, cb):
            self._stop_cb = cb

        async def start(self):
            self.started = True

        async def stop(self):
            self.stopped = True

    monkeypatch.setattr(trader_mod, "ControlServer", MockControlServer)

    # Prevent async_cli from calling builtins.exit() which would raise SystemExit
    monkeypatch.setattr(builtins, "exit", lambda code=0: None)

    orch = orchestrator

    # Run async_cli in background
    task = asyncio.create_task(trader_mod.async_cli(orch, control_token="fake-token"))

    # allow it to start
    await asyncio.sleep(0.05)

    # Be resilient to different mock shapes: some use `is_running`, others
    # `started`. Prefer boolean attribute values when present.
    if hasattr(orch, "__dict__"):
        running = orch.__dict__.get("is_running", orch.__dict__.get("started"))
    else:
        running = getattr(orch, "is_running", getattr(orch, "started", None))

    # Fallback to getattr if still None
    if running is None:
        running = getattr(orch, "is_running", getattr(orch, "started", None))

    assert running is True

    # cancel and wait for cleanup; async_cli handles CancelledError internally
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        # If the task still propagates cancellation, that's acceptable.
        pass

    # ensure cleanup happened: check either `stopped` flag (explicit) or
    # that the running flag flipped to False.
    if hasattr(orch, "__dict__"):
        running_after = orch.__dict__.get("is_running", orch.__dict__.get("started"))
        stopped_flag = orch.__dict__.get("stopped")
    else:
        running_after = getattr(orch, "is_running", getattr(orch, "started", None))
        stopped_flag = getattr(orch, "stopped", None)

    # allow either explicit stopped flag or running==False
    assert (stopped_flag is True) or (running_after is False)


def test_stop_trader_cli_success_and_fallback(tmp_path, monkeypatch):
    """Test that stop_trader.cli uses control.meta and prefers control token and falls back to PID kill."""

    # Provide a minimal portalocker shim for the test environment
    fake_portalocker = types.SimpleNamespace()

    def _lock(handle, flags):
        return None

    def _unlock(handle):
        return None

    class LockException(Exception):
        pass

    fake_portalocker.lock = _lock
    fake_portalocker.unlock = _unlock
    fake_portalocker.LOCK_EX = 1
    fake_portalocker.LOCK_NB = 2
    fake_portalocker.exceptions = types.SimpleNamespace(LockException=LockException)

    monkeypatch.setitem(sys.modules, "portalocker", fake_portalocker)

    stop_mod = importlib.import_module(STOP_CLI_MODULE)

    # Write control.meta next to the stop_trader module so cli() will find it.
    # Guard against a missing __file__ and ensure dirname receives a str
    module_file = getattr(stop_mod, "__file__", None)
    if not module_file:
        pytest.skip("stop_trader module has no __file__; skipping")
    meta_file = os.path.join(os.path.dirname(str(module_file)), "..", "control.meta")
    control_meta_path = os.path.abspath(meta_file)
    os.makedirs(os.path.dirname(control_meta_path), exist_ok=True)
    meta = {"host": "127.0.0.1", "port": 9999}
    with open(control_meta_path, "w") as f:
        json.dump(meta, f)

    # Mock requests.post to return success
    class Resp:
        def __init__(self, code):
            self.status_code = code

    called = {"stopped": False, "post_called": False}

    def fake_post_success(url, headers=None, timeout=None):
        called["post_called"] = True
        return Resp(200)

    # Patch the requests.post used inside stop_trader module directly to be
    # certain the function invoked by cli() is our fake.
    monkeypatch.setattr(stop_mod.requests, "post", fake_post_success)

    def fake_stop_process(lock_file: str):
        called["stopped"] = True

    monkeypatch.setattr(stop_mod, "stop_process", fake_stop_process)

    # call cli; should hit requests.post (we assert the post was invoked)
    lock_file = str(tmp_path / "trader_dev_integration.lock")
    stop_mod.cli(lock_file=lock_file, env="dev_integration")
    assert called["post_called"] is True

    # Now simulate requests.post raising -> fall back to stop_process
    def fake_post_raise(url, headers=None, timeout=None):
        raise RuntimeError("connection failed")

    monkeypatch.setattr(stop_mod.requests, "post", fake_post_raise)

    stop_mod.cli(lock_file=lock_file, env="dev_integration")
    assert called["stopped"] is True

    # cleanup
    try:
        os.remove(control_meta_path)
    except Exception:
        pass
