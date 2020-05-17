from panoramisk.message import Message
from sanic import Blueprint
from sanic.log import logger
from sanic.request import Request
from sanic.response import json, HTTPResponse

from app.asterisk import manager

api = Blueprint('API', url_prefix='/api/v1', strict_slashes=True)


@api.post('/action/')
async def action(request: Request) -> HTTPResponse:
    logger.info(f'data: {request.json}')
    result = await manager.send_action(request.json)
    logger.info(f'result: {result}')
    if isinstance(result, list):
        result = [{**i} for i in result]
    elif isinstance(result, Message):
        result = {**result}
    else:
        result = f'{result}'
    return json({'data': result, 'status': 'ok'})
