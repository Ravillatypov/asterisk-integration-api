from sanic import Sanic
from tortoise.contrib.sanic import register_tortoise

from app.asterisk import register_manager
from app.settings import DB_URL, IS_DEV
from app.api.actions import api

app = Sanic('Asterisk Integration API')
register_tortoise(app, db_url=DB_URL, modules={'models': ['app.models']}, generate_schemas=True)
register_manager(app)
app.blueprint(api)

if __name__ == '__main__':
    app.run('0.0.0.0', 8000, auto_reload=IS_DEV)
