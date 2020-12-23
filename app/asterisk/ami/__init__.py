import logging

from panoramisk import Manager
from app.settings import CAPTURE_EVENTS
from . import v1_3, v2_8, v4_0, v5_0, capture


def register(manager: Manager):
    major, minor = manager.protocol.version.split('.')[:2]
    version = f'{major}.{minor}'
    logging.info(f'protocol version: {version}')

    if CAPTURE_EVENTS:
        capture.register(manager, CAPTURE_EVENTS)

    if '1.3' == version:
        v1_3.register(manager)
    elif '2.8' == version:
        v2_8.register(manager)
    elif '4.0' == version:
        v4_0.register(manager)
    elif '5.0' == version:
        v5_0.register(manager)
    else:
        logging.warning(f'Not found register function for version: {version}')


__all__ = ['register']
