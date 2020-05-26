import logging
from asyncio import sleep

from aiomisc.log import JSONLogFormatter
from aiomisc.service.base import Service
from panoramisk.manager import Manager

from ..asterisk.ami import register
from ..settings import PORT, LOGIN, SECRET, IP, AMI_LOG_PATH

logger = logging.getLogger('ami')
file_handler = logging.FileHandler(AMI_LOG_PATH)
file_handler.setFormatter(JSONLogFormatter(datefmt=None))
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

manager = Manager(host=IP, port=PORT, log=logger, username=LOGIN, secret=SECRET, ping_delay=1)
queue_numbers = []


class AMIService(Service):
    async def start(self):
        manager.loop = self.loop
        await manager.connect()

        for _ in range(100):
            if manager.protocol.version:
                break
            await sleep(0.3)
        else:
            if not manager.protocol.version:
                raise Exception('AMI connection is unavailable')
        register(manager)

    async def stop(self, *args, **kwargs):
        manager.close()


__all__ = ['manager', 'AMIService']
