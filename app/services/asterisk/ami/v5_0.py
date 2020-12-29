from datetime import datetime
from typing import Optional

from panoramisk.manager import Manager
from panoramisk.message import Message

from app.services.asterisk.utils import get_number, is_internal, is_external
from app.consts import CallType, CallState
from app.models import Call


async def _get_call(message: Message) -> Optional[Call]:
    return await Call.get_or_none(id=message.get('Linkedid', ''))


async def new_channel(manager: Manager, message: Message):
    if message.get('Uniqueid', '') != message.get('Linkedid', ''):
        return

    src_num = get_number(message.get('CallerIDNum', ''))
    dst_num = get_number(message.get('Exten', ''))

    call_type = CallType.UNKNOWN
    from_pin = from_num = request_num = request_pin = ''

    if is_internal(src_num) and is_internal(dst_num):
        call_type = CallType.INTERNAL
        from_pin = src_num
        request_pin = dst_num
    elif is_internal(src_num) and is_external(dst_num):
        call_type = CallType.OUTBOUND
        from_pin = src_num
        request_num = dst_num
    elif is_external(src_num):
        call_type = CallType.INCOMING
        from_num = src_num
        request_num = dst_num

    await Call.create(
        id=message.get('Linkedid', ''),
        from_pin=from_pin,
        from_number=from_num,
        request_number=request_num,
        request_pin=request_pin,
        call_type=call_type,
        state=CallState.NEW,
        created_at=datetime.utcnow(),
    )


async def hangup(manager: Manager, message: Message):
    call = await _get_call(message)

    if not call or call.state in (CallState.NOT_CONNECTED, CallState.MISSED, CallState.END):
        return

    call.finished_at = datetime.utcnow()

    if call.state == CallState.CONNECTED:
        call.state = CallState.END
    elif call.call_type == CallType.INCOMING:
        call.state = CallState.MISSED
    else:
        call.state = CallState.NOT_CONNECTED

    await call.save()


async def dial_end(manager: Manager, message: Message):
    if message.get('DialStatus', '') != 'ANSWER':
        return

    call = await _get_call(message)
    if not call:
        return

    call.state = CallState.CONNECTED
    call.voice_started_at = datetime.utcnow()

    request_pin = get_number(message.get('DestCallerIDNum', ''))
    if call.call_type == CallType.INCOMING and is_internal(request_pin):
        call.request_pin = request_pin

    await call.save()


async def agent_called(manager: Manager, message: Message):
    request_pin = message.get('Queue', '') or message.get('Exten', '')
    call = await _get_call(message)

    if not call:
        return

    if call.call_type != CallType.INCOMING:
        call.call_type = CallType.INCOMING

    if not call.request_pin:
        call.request_pin = get_number(request_pin)

    if call.state != CallState.NEW:
        call.state = CallState.NEW

    await call.save()


def register(manager: Manager):
    manager.register_event('Hangup', hangup)
    manager.register_event('Newchannel', new_channel)
    manager.register_event('AgentCalled', agent_called)
    manager.register_event('DialEnd', dial_end)