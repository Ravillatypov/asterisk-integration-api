from tortoise.backends.base.client import BaseDBAsyncClient

version = 1


async def upgrade(conn: BaseDBAsyncClient):
    await conn.execute_query(
        'ALTER TABLE "calls" ADD COLUMN record_path varchar(255) default null;'
    )


async def downgrade(conn: BaseDBAsyncClient):
    pass
