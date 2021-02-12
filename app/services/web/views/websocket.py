from aiohttp import web
from aiohttp_cors import ResourceOptions, CorsViewMixin

from app.misc.logging import get_logger
from app.services.websocket import WSInterface


logger = get_logger('websocket', 'INFO')


class CallsWSView(web.View, CorsViewMixin):
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

        WSInterface.ws_clients.append(ws)
        logger.info(f'New WS connection. WS counts: {len(WSInterface.ws_clients)}')

        async for msg in ws:
            pass

        try:
            WSInterface.ws_clients.remove(ws)
        except Exception as err:
            logger.warning('Close error', err=err)

        return ws
