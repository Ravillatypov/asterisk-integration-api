from aiohttp import web

from app.services.websocket import WSInterface
from .base import BaseClientAuthView


class WSView(BaseClientAuthView):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        WSInterface.ws_clients.add(ws)

        async for msg in ws:
            pass

        WSInterface.ws_clients.remove(ws)

        return ws

    async def _get_access_token(self) -> str:
        return self.request.query.get('token', '')
