import asyncio
import pytest
from aiohttp import ClientSession

from algo_royale.utils.control_server import ControlServer


@pytest.mark.asyncio
async def test_control_server_stop_endpoint(tmp_path):
    """Start ControlServer and verify /status and /stop with token and callback."""
    token = 'test-token-123'
    server = ControlServer(token=token, host='127.0.0.1', port=0)

    stopped = asyncio.Event()

    async def stop_cb():
        stopped.set()

    server.set_stop_callback(stop_cb)

    # start server (port=0 => ephemeral port assigned)
    await server.start()

    host = server.host
    port = server.port
    assert host == '127.0.0.1'
    assert port != 0

    url = f'http://{host}:{port}'

    async with ClientSession() as session:
        # status
        async with session.get(f'{url}/status') as r:
            assert r.status == 200
            j = await r.json()
            assert j['status'] == 'running'

        # stop without token -> forbidden
        async with session.post(f'{url}/stop') as r:
            assert r.status == 403

        # stop with token header -> accepted and triggers callback
        headers = {'X-ALGO-TOKEN': token}
        async with session.post(f'{url}/stop', headers=headers) as r:
            assert r.status == 200
            j = await r.json()
            assert j['status'] == 'stopping'

    # wait shortly for callback to run
    await asyncio.wait_for(stopped.wait(), timeout=2.0)

    # cleanup
    await server.stop()
