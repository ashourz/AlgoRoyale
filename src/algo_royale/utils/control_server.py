import asyncio
from aiohttp import web
import os
import json

# Simple control server for trader process. Binds to localhost and requires a token
# passed via env var ALGO_ROYALE_CONTROL_TOKEN (if set). Exposes /stop and /status.

class ControlServer:
    def __init__(self, token: str, host='127.0.0.1', port=8765):
        self.host = host
        self.port = port
        self._app = web.Application()
        self._runner = None
        self._site = None
        self._stop_cb = None
        # token provided explicitly (preferred) otherwise fall back to env
        self._token = token
        self._app.add_routes([
            web.get('/status', self._handle_status),
            web.post('/stop', self._handle_stop),
        ])

    async def _handle_status(self, request):
        return web.json_response({'status': 'running'})

    async def _handle_stop(self, request):
        # optional token check
        if self._token:
            header = request.headers.get('X-ALGO-TOKEN')
            if not header or header != self._token:
                return web.Response(status=403, text='forbidden')

        # trigger user-provided stop callback
        if self._stop_cb:
            asyncio.create_task(self._stop_cb())
            return web.json_response({'status': 'stopping'})
        return web.json_response({'status': 'no-op'})

    def set_stop_callback(self, cb):
        self._stop_cb = cb

    async def start(self):
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()
        # If an ephemeral port was requested (port=0), the actual bound port
        # will be available on the site's server sockets after start(). Update
        # self.port so callers can inspect the assigned port.
        try:
            server = getattr(self._site, '_server', None)
            sockets = getattr(server, 'sockets', None) if server is not None else None
            if sockets:
                # take the first socket's port
                sock = sockets[0]
                addr = sock.getsockname()
                # getsockname may return (host, port) or (host, port, ...)
                if isinstance(addr, tuple) and len(addr) >= 2:
                    self.port = int(addr[1])
        except Exception:
            # best-effort only; don't fail start if introspection is not possible
            pass
        # write metadata for client discovery
        try:
            meta = {'host': self.host, 'port': self.port}
            meta_file = os.path.join(os.path.dirname(__file__), '..', 'control.meta')
            with open(meta_file, 'w') as f:
                json.dump(meta, f)
        except Exception:
            pass

    async def stop(self):
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()
        # remove metadata
        try:
            meta_file = os.path.join(os.path.dirname(__file__), '..', 'control.meta')
            if os.path.exists(meta_file):
                os.remove(meta_file)
        except Exception:
            pass

    # synchronous convenience helpers
    def run_in_background(self, loop):
        # start coroutine in given loop
        return loop.create_task(self.start())
