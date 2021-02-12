from aiohttp import web
from aiohttp_cors import ResourceOptions, CorsViewMixin

from app.services.websocket import WSInterface


class WSView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    }

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        WSInterface.ws_clients.add(ws)

        async for msg in ws:
            pass

        WSInterface.ws_clients.remove(ws)

        return ws
