from uuid import uuid4

from panoramisk.actions import Action as BaseAction
from panoramisk.message import Message

from . import manager
from app.config import app_config


class Action(BaseAction):
    @property
    def multi(self):
        resp = self.responses[0]
        msg = resp.message.lower()
        if self.as_list is not None:
            return bool(self.as_list)
        elif resp.subevent == 'Start':
            return True
        elif resp.get('EventList', '') == 'start':
            return True
        elif 'will follow' in msg:
            return True
        elif msg.startswith('added') and msg.endswith('to queue'):
            return True
        elif msg.endswith('successfully queued') and self.get('async', '') != 'false':
            return True
        return False


async def make_call(from_pin: str, request_number: str) -> str:
    account_id = f'{uuid4()}'
    if not request_number.startswith(app_config.ats.start_digit):
        request_number = app_config.ats.start_digit + request_number[1:]

    action = Action(
        Action='Originate',
        Channel=f'{app_config.ats.transport}/{from_pin}',
        Exten=request_number,
        Priority=1,
        Context=app_config.ats.context,
        Callerid=request_number,
        Account=account_id
    )
    res = await manager.send_action(action)
    return account_id if isinstance(res, Message) and res.sucess else ''
