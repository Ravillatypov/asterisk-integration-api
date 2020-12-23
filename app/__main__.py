import logging
from logging.handlers import TimedRotatingFileHandler

from aiomisc import entrypoint, receiver
from prettylog import JSONLogFormatter
from tortoise import Tortoise

from .api import WebService
from .asterisk import AMIService
from .call_records import services as record_services
from .services import services as ws_services
from .settings import DB_URL, LOG_PATH, LOG_LEVEL

logging.basicConfig()
logger = logging.getLogger()
logger.handlers.clear()
handler = TimedRotatingFileHandler(LOG_PATH, when='d', backupCount=30)
handler.setFormatter(JSONLogFormatter())
logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[handler],
)


@receiver(entrypoint.PRE_START)
async def start_up(*args, **kwargs):
    await Tortoise.init(modules={'models': ['app.models']}, db_url=DB_URL)
    await Tortoise.generate_schemas()


@receiver(entrypoint.POST_STOP)
async def shutdown(*args, **kwargs):
    await Tortoise.close_connections()


services = (
    AMIService(),
    WebService('0.0.0.0', 8000),
    *record_services,
    *ws_services,
)

if __name__ == '__main__':
    with entrypoint(*services) as loop:
        loop.run_forever()
