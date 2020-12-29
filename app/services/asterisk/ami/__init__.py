from panoramisk import Manager

from app.config import app_config
from app.misc.logging import get_logger
from . import v1_3, v2_8, v4_0, v5_0, capture

logger = get_logger('app')


def register(manager: Manager):
    major, minor = manager.protocol.version.split('.')[:2]
    version = f'{major}.{minor}'
    logger.info(f'protocol version: {version}')

    if app_config.ami.capture:
        capture.register(manager, app_config.ami.capture)

    if '1.3' == version:
        v1_3.register(manager)
    elif '2.8' == version:
        v2_8.register(manager)
    elif '4.0' == version:
        v4_0.register(manager)
    elif '5.0' == version:
        v5_0.register(manager)
    else:
        logger.warning(f'Not found register function for version: {version}')


__all__ = ['register']
