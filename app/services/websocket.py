from asyncio import sleep, Lock
from asyncio.queues import Queue
from collections import defaultdict
from typing import Dict, Any, Set, List, Optional, Type
from uuid import uuid4

from aiohttp import WSMsgType
from aiohttp.client import ClientSession
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.web_ws import WebSocketResponse
from aiomisc.service.base import Service
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save

from app.services.asterisk.manager_utils import make_call
from ..config import app_config
from ..misc.logging import get_logger
from ..models import Call

logger = get_logger('websocket')


async def post_event(event: dict):
    if not app_config.events.url:
        return

    try:
        async with ClientSession(headers=app_config.events.headers) as session:
            async with session.post(app_config.events.url, json=event) as resp:
                logger.info('send event status', response_status=resp.status)
    except Exception as err:
        logger.warning('Error on send event (post)', err=err)


class WSInterface:
    ws: ClientWebSocketResponse
    ws_clients: Set[WebSocketResponse] = {}
    need_stop: bool = not bool(app_config.events.ws_url)
    responses: Dict[str, Any] = {}  # result from server
    events: Queue = Queue()  # events and request to remote server
    commands: Queue = Queue()  # commands from remote server

    def __new__(cls, *args, **kwargs):
        return None

    @classmethod
    async def request(cls, data: dict) -> Any:
        request_id = f'{uuid4()}'
        await cls.events.put({
            'request_id': request_id,
            'data': data,
        })

        return request_id

    @classmethod
    async def wait_result(cls, request_id: str) -> Any:
        while request_id not in cls.responses:
            await sleep(0.005)
        return cls.responses.pop(request_id)

    @classmethod
    async def add_event(cls, data):
        if not cls.need_stop:
            await cls.events.put({
                'data': data,
                'type': 'event',
            })

        await post_event(data)
        for ws in cls.ws_clients:
            await ws.send_json(data)


pre_events = defaultdict(dict)
event_lock = Lock()


@post_save(Call)
async def post_save_call(
        sender: "Type[Call]",
        instance: Call,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str]
):
    event = instance.event_schema()
    if pre_events[instance.id] != event:
        await event_lock.acquire()
        pre_events[instance.id] = event
        event_lock.release()
        await WSInterface.add_event(event)

    if instance.is_finished and instance.id in pre_events:
        await event_lock.acquire()
        pre_events.pop(instance.id)
        event_lock.release()


class WSService(Service):
    async def start(self):
        while not WSInterface.need_stop:
            await self.handler()

    async def handler(self):
        raise NotImplementedError

    async def stop(self, exception: Exception = None):
        WSInterface.need_stop = True
        if WSInterface.ws and not WSInterface.ws.closed:
            await WSInterface.ws.close()


class WSReaderService(WSService):
    async def handler(self):
        await sleep(1)
        try:
            async with ClientSession(headers=app_config.events.ws_headers) as session:
                async with session.ws_connect(app_config.events.ws_url,
                                              receive_timeout=60,
                                              heartbeat=35.0,
                                              autoclose=True) as ws:
                    WSInterface.ws = ws
                    await self._message_handler()
        except Exception as err:
            logger.warning('WS closed with error', err=err)

    @staticmethod
    async def _message_handler():
        async for msg in WSInterface.ws:
            if msg.type == WSMsgType.TEXT:
                data = msg.json()
                if data.get('response_id'):
                    WSInterface.responses[data.get('response_id')] = data
                elif data.get('request_id'):
                    await WSInterface.commands.put(data)
                else:
                    logger.warning('Bad message from server', message=msg)
            else:
                logger.warning('Bad message', type=msg.type)


class WSWriterService(WSService):
    async def handler(self):
        if not WSInterface.ws or WSInterface.ws.closed:
            await sleep(1)
            return

        msg = await WSInterface.events.get()
        try:
            await WSInterface.ws.send_json(msg)
        except TypeError as err:
            logger.warning('Message is not serializable', message=msg, err=err)
        except Exception as err:
            if not WSInterface.ws or WSInterface.ws.closed:
                await WSInterface.events.put(msg)
            logger.warning('Can`t send message', err=err)


class CommandService(WSService):
    async def handler(self):
        cmd = await WSInterface.commands.get()
        cmd_type = cmd.get('type')
        data = cmd.get('data')
        if cmd_type == 'callback':
            res = await make_call(data.get('from_pin', ''), data.get('request_number', ''))
            await WSInterface.events.put({
                'response_id': cmd.get('request_id', ''),
                'success': bool(res),
                'result': res,
            })
