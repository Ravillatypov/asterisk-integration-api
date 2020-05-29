from aiohttp.web_app import Application
from aiomisc.service.aiohttp import AIOHTTPService
from aiohttp_swagger import setup_swagger

from .views import setup_router


class WebService(AIOHTTPService):
    async def create_application(self) -> Application:
        app = Application()
        setup_router(app)
        setup_swagger(app, ui_version=3, swagger_url='/docs', title='Asterisk Service API')
        return app


__all__ = ['WebService']
