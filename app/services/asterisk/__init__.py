from asyncio import sleep

from aiomisc.service.base import Service
from panoramisk.manager import Manager

from ..asterisk.ami import register
from app.config import app_config
from app.misc.logging import get_logger

logger = get_logger('ami')

manager = None

if app_config.ami.enabled:
    manager = Manager(
        host=app_config.ami.ip,
        port=app_config.ami.port,
        log=logger,
        username=app_config.ami.login,
        secret=app_config.ami.secret,
        ping_delay=1
    )


class AMIService(Service):
    async def start(self):
        if not app_config.ami.enabled:
            return

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
        if isinstance(manager, Manager):
            manager.close()


__all__ = ['manager', 'AMIService']
