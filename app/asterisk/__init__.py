import logging
from asyncio import sleep

from panoramisk.manager import Manager
from sanic import Sanic

from app.asterisk.ami import register
from app.settings import PORT, LOGIN, SECRET, IP, AMI_LOG_PATH

logger = logging.getLogger('ami')
formatter = logging.Formatter('%(asctime)s; %(message)s')
file_handler = logging.FileHandler(AMI_LOG_PATH)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


manager = Manager(host=IP, port=PORT, log=logger, username=LOGIN, secret=SECRET, ping_delay=1)
queue_numbers = []


def register_manager(app: Sanic) -> None:

    @app.listener("before_server_start")
    async def connect_to_ami(app, loop):
        manager.loop = loop
        await manager.connect()

        for _ in range(100):
            if manager.protocol.version:
                break
            await sleep(0.3)
        else:
            if not manager.protocol.version:
                raise Exception('AMI connection is unavailable')
        register(manager)

    @app.listener("after_server_stop")
    async def close_connection(app, loop):
        manager.close()


__all__ = ['manager', 'register_manager']
