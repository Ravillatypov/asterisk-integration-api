import json
from datetime import datetime
from typing import Tuple

from aiomisc.io import async_open
from panoramisk import Manager
from panoramisk.message import Message
from app.config import app_config


async def capture_message(manager: Manager, message: Message):
    now = datetime.utcnow().strftime('%Y-%m-%d')
    try:
        async with async_open(f'{app_config.log_path}/messages-{now}.txt', 'a') as f:
            await f.write(json.dumps(dict(message)) + '\n')
    except Exception:
        pass


def register(manager: Manager, events: Tuple[str]):
    for event in events:
        manager.register_event(event, capture_message)
