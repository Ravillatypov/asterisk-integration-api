from asyncio import sleep
from typing import Dict

from panoramisk.manager import Manager
from panoramisk.message import Message


async def handle_message(manager: Manager, data: Dict[str, str]):
    message = Message(data)
    manager.protocol.handle_message(message)
    await sleep(0.03)
