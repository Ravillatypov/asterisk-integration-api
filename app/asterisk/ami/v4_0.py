from panoramisk.manager import Manager
from panoramisk.message import Message


async def var_set(manager: Manager, message: Message):
    pass


async def new_channel(manager: Manager, message: Message):
    pass


async def new_state(manager: Manager, message: Message):
    pass


async def new_exten(manager: Manager, message: Message):
    pass


async def hangup(manager: Manager, message: Message):
    pass


async def bridge(manager: Manager, message: Message):
    pass


async def dial(manager: Manager, message: Message):
    pass


async def masquerade(manager: Manager, message: Message):
    pass


async def join(manager: Manager, message: Message):
    pass


async def leave(manager: Manager, message: Message):
    pass


def register(manager: Manager):
    manager.register_event('Bridge', bridge)
    manager.register_event('Dial', dial)
    manager.register_event('Hangup', hangup)
    manager.register_event('Join', join)
    manager.register_event('Leave', leave)
    manager.register_event('Masquerade', masquerade)
    manager.register_event('Newchannel', new_channel)
    manager.register_event('Newstate', new_state)
    manager.register_event('VarSet', var_set)
