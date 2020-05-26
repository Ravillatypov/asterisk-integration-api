import logging

from aiomisc import entrypoint, receiver
from aiomisc.log import basic_config
from tortoise import Tortoise

from .api import WebService
from .asterisk import AMIService
from .settings import DB_URL

basic_config(level=logging.INFO, buffered=False, log_format='json')


@receiver(entrypoint.PRE_START)
async def start_up(*args, **kwargs):
    await Tortoise.init(modules={'models': ['app.models']}, db_url=DB_URL)
    await Tortoise.generate_schemas()


@receiver(entrypoint.POST_STOP)
async def shutdown(*args, **kwargs):
    await Tortoise.close_connections()


if __name__ == '__main__':
    with entrypoint(AMIService(), WebService('0.0.0.0', 8000)) as loop:
        loop.run_forever()
