import asyncio
from os import remove
from uuid import uuid4

import pytest
from panoramisk.testing import Manager
from tortoise import Tortoise

from app.asterisk.ami import register


@pytest.fixture
def loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    path = f'/tmp/test_{uuid4()}.sqlite3'

    async def init():
        await Tortoise.init(modules={'models': ['app.models']}, db_url=f'sqlite://{path}')
        await Tortoise.generate_schemas()

    loop.run_until_complete(init())
    yield loop

    loop.run_until_complete(Tortoise.close_connections())
    loop.close()
    remove(path)


@pytest.fixture
def manager_v1_3(loop):
    m = Manager(loop=loop)
    m.protocol.version = '1.3.0'
    register(m)
    return m


@pytest.fixture
def manager_v2_8(loop):
    m = Manager(loop=loop)
    m.protocol.version = '2.8.4'
    register(m)
    return m


@pytest.fixture
def manager_v4_0(loop):
    m = Manager(loop=loop)
    m.protocol.version = '4.0.1'
    register(m)
    return m
