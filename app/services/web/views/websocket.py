from aiohttp import web

from app.services.websocket import WSInterface


class WSView(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        WSInterface.ws_clients.add(ws)

        async for msg in ws:
            pass

        WSInterface.ws_clients.remove(ws)

        return ws
