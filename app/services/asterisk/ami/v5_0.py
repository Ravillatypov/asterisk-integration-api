from datetime import datetime
from typing import Optional

from panoramisk.manager import Manager
from panoramisk.message import Message

from app.consts import CallType, CallState
from app.models import Call, CallRecord, Channel
from app.services.asterisk.utils import get_number, is_internal, is_external, is_group_numbers, get_company_id
from app.utils import get_full_path


async def _get_call(message: Message) -> Optional[Call]:
    return await Call.all().prefetch_related('tags', 'records').get_or_none(id=message.get('Linkedid', ''))


async def var_set(manager: Manager, message: Message):
    if message.get('Variable', '') != 'MIXMONITOR_FILENAME':
        return

    call = await _get_call(message)
    if not call:
        return

    var_file_name = message.get('Value', '')
    monitor_file_name = get_full_path(var_file_name)
    manager.log.info(f'record_file: {monitor_file_name}, call_id: {call.id}')

    ch, _ = await Channel.get_or_create(
        defaults={
            'name': message.get('Channel'),
            'call': call,
            'monitor_file_name': monitor_file_name,
        },
        id=message.get('Uniqueid'),
    )

    record = await CallRecord.create(
        call=call,
        channel=ch,
        file_name=monitor_file_name,
    )

    if monitor_file_name:
        call.record = record
        await call.save()


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
        company_id=get_company_id(from_pin, from_num, request_pin, request_num),
    )


async def hangup(manager: Manager, message: Message):
    if message.get('Uniqueid', '') != message.get('Linkedid', ''):
        return

    call = await _get_call(message)

    if not call or call.state in (CallState.NOT_CONNECTED, CallState.MISSED, CallState.END):
        return

    call.finished_at = datetime.utcnow()

    caller_name = message.get('CallerIDName', '')
    caller_num = message.get('CallerIDNum', '')

    if caller_name != '<unknown>' and caller_num and caller_num in (call.from_pin, call.request_pin):
        call.user = caller_name

    if call.state == CallState.CONNECTED:
        call.state = CallState.END

    elif call.call_type == CallType.INCOMING:
        call.state = CallState.MISSED

    else:
        call.state = CallState.NOT_CONNECTED

    call.company_id = get_company_id(call.from_pin, call.from_number, call.request_pin, call.request_number)

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
    if call.call_type == CallType.INCOMING and \
            is_internal(request_pin) and \
            (not call.request_pin or not is_group_numbers(request_pin)):
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
    manager.register_event('VarSet', var_set)
