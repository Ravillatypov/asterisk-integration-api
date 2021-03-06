import asyncio
from shutil import rmtree
from uuid import uuid4

import pytest
from panoramisk.testing import Manager
from tortoise import Tortoise

from app.services.asterisk.ami import register


@pytest.fixture
def loop(tmp_path):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    path = tmp_path.as_posix() + f'/{uuid4()}.sqlite3'

    async def init():
        await Tortoise.init(modules={'models': ['app.models']}, db_url=f'sqlite://{path}')
        await Tortoise.generate_schemas()

    loop.run_until_complete(init())
    yield loop

    async def drop():
        await Tortoise._drop_databases()
        await Tortoise.close_connections()

    loop.run_until_complete(drop())
    rmtree(tmp_path.as_posix(), True)
    loop.close()


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
