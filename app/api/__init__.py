from aiohttp.web_app import Application
from aiomisc.service.aiohttp import AIOHTTPService

from .views import setup_router


class WebService(AIOHTTPService):
    async def create_application(self) -> Application:
        app = Application()
        setup_router(app)
        return app


__all__ = ['WebService']
