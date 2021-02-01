import json

from aiohttp.web_app import Application
from aiohttp_swagger import setup_swagger
from aiomisc.service.aiohttp import AIOHTTPService

from .spec import definitions, parameters
from .views import setup_router


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

        self._set_parameters(app, parameters)

        return app

    @staticmethod
    def _set_parameters(app: Application, params: dict = None):
        try:
            prev_doc = app['SWAGGER_DEF_CONTENT']
            data = json.loads(prev_doc)
            data['components']['parameters'] = params
            app['SWAGGER_DEF_CONTENT'] = json.dumps(data, ensure_ascii=True, indent=2)
        except Exception:
            pass


__all__ = ['WebService']
