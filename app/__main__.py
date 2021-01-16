import sentry_sdk
from aiomisc import entrypoint, receiver
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from .config import app_config
from .misc.hooks import init_db, close_db
from .services import services

if app_config.sentry_dsn:
    sentry_sdk.init(app_config.sentry_dsn, release=app_config.release, integrations=[AioHttpIntegration()])


@receiver(entrypoint.PRE_START)
async def start_up(*args, **kwargs):
    await init_db()


@receiver(entrypoint.POST_STOP)
async def shutdown(*args, **kwargs):
    await close_db()


if __name__ == '__main__':
    with entrypoint(*services) as loop:
        try:
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
