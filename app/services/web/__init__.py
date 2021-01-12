from aiohttp.web_app import Application
from aiohttp_swagger import setup_swagger
from aiomisc.service.aiohttp import AIOHTTPService

from .views import setup_router
from .spec import definitions


class WebService(AIOHTTPService):
    async def create_application(self) -> Application:
        app = Application()
        setup_router(app)
        setup_swagger(
            app,
            ui_version=3,
            swagger_url='/api/docs',
            title='Asterisk Service API',
            description='Asterisk Service API',
            definitions=definitions,
            security_definitions={
                'jwt': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header',
                }
            },
        )
        return app


__all__ = ['WebService']
