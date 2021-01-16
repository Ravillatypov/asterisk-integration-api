from tortoise import Tortoise

from app.config import app_config


async def init_db(*args, **kwargs):
    await Tortoise.init(modules={'models': ['app.models']}, db_url=app_config.db_url)
    await Tortoise.generate_schemas()


async def close_db(*args, **kwargs):
    await Tortoise.close_connections()
