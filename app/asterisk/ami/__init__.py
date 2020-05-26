import logging

from panoramisk import Manager

from . import v1_3, v2_8, v4_0


def register(manager: Manager):
    major, minor = manager.protocol.version.split('.')[:2]
    version = f'{major}.{minor}'
    logging.info(f'protocol version: {version}')

    if '1.3' == version:
        v1_3.register(manager)
    elif '2.8' == version:
        v2_8.register(manager)
    elif '4.0' == version:
        v4_0.register(manager)
    else:
        logging.warning(f'Not found register function for version: {version}')


__all__ = ['register']
