from aiohttp.web_app import Application
from aiomisc.service.aiohttp import AIOHTTPService
from .views import router


class WebService(AIOHTTPService):
    async def create_application(self) -> Application:
        app = Application()
        app.add_routes(router)
        return app


__all__ = ['WebService']
