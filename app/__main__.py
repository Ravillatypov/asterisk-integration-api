import sentry_sdk
from aiomisc import entrypoint, receiver
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from tortoise import Tortoise

from .config import app_config
from .services import services

if app_config.sentry_dsn:
    sentry_sdk.init(app_config.sentry_dsn, release=app_config.release, integrations=[AioHttpIntegration()])


@receiver(entrypoint.PRE_START)
async def start_up(*args, **kwargs):
    await Tortoise.init(modules={'models': ['app.models']}, db_url=app_config.db_url)
    await Tortoise.generate_schemas()


@receiver(entrypoint.POST_STOP)
async def shutdown(*args, **kwargs):
    await Tortoise.close_connections()


if __name__ == '__main__':
    with entrypoint(*services) as loop:
        try:
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
