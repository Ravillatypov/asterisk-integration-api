from tortoise import Tortoise

from app.config import app_config

TORTOISE_ORM = {
    'connections': {'default': app_config.db_url},
    'apps': {
        'models': {
            'models': ['app.models', 'aerich.models'],
            'default_connection': 'default',
        },
    },
}


async def init_db(*args, **kwargs):
    await Tortoise.init(TORTOISE_ORM)
    # await Tortoise.generate_schemas()


async def close_db(*args, **kwargs):
    await Tortoise.close_connections()
