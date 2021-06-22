from datetime import datetime

from panoramisk.manager import Manager
from panoramisk.message import Message

from ..cache import calls, channels
from ..utils import validate_numbers, get_call_type, is_group_numbers, get_internal
from app.config import app_config
from app.consts import CallState, CallType
from app.models import Channel, Call, CallRecord


async def var_set(manager: Manager, message: Message):
    if message.get('Variable', '') != 'MIXMONITOR_FILENAME':
        return
    ch = channels.get(message.get('Uniqueid', ''))
    if not ch:
        return

    ch.monitor_file_name = message.get('Value')[-255:]
    await ch.save()

    call = calls.get(ch.id, ch.call)
    if not call:
        ch2 = await ch.bridged.filter(call=None).first()
        call = ch2.call if ch2 else call

    await CallRecord.create(
        call=call,
        channel=ch,
        file_name=ch.monitor_file_name,
    )


async def new_channel(manager: Manager, message: Message):
    num = validate_numbers(message.get('CallerIDNum'), message.get('Exten'))
    call = None

    if 'from-queue' not in message.get('Context', '') and num:
        call = await Call.create(
            id=message.get('Uniqueid'),
            state=CallState.NEW,
            from_pin=num.from_pin,
            from_number=num.from_number,
            request_number=num.request_number,
            request_pin=num.request_pin,
            call_type=get_call_type(num),
            account_id=message.get('AccountCode'),
        )
        calls[call.id] = call

    ch = await Channel.create(
        id=message.get('Uniqueid'),
        name=message.get('Channel'),
        from_number=num.src,
        request_number=num.dst,
        call=call,
    )
    channels[ch.id] = ch


async def new_state(manager: Manager, message: Message):
    state = message.get('ChannelState', '')
    num = validate_numbers(message.get('CallerIDNum', ''), message.get('ConnectedLineNum', ''))
    call = calls.get(message.get('Uniqueid', ''))

    if not call or not num or state != '6' or is_group_numbers(num.request_pin):
        return

    call.state = CallState.CONNECTED
    call.voice_started_at = datetime.now()
    call.account_id = call.account_id or message.get('AccountCode')

    src_nums = (call.from_pin, call.from_number)
    dst_nums = (call.request_pin, call.request_number)

    if call.call_type == CallType.INCOMING:
        if num.src in src_nums and num.dst not in dst_nums:
            call.request_number = call.request_number or num.request_number
            call.request_pin = num.request_pin or call.request_pin
        elif num.dst in src_nums and num.src not in dst_nums:
            call.request_number = call.request_number or num.from_number
            call.request_pin = num.from_pin or call.request_pin

    await call.save()


async def hangup(manager: Manager, message: Message):
    u_id = message.get('Uniqueid')
    call = calls.get(u_id)

    if u_id in channels:
        channels.pop(u_id)

    if not call:
        return

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

    call.finished_at = datetime.now()
    call.account_id = call.account_id or message.get('AccountCode')

    await call.save()

    calls.pop(call.id)


async def bridge(manager: Manager, message: Message):
    if message.get('Bridgestate', '') not in ('Link', 'Unlink'):
        return

    b1 = channels.get(message.get('Uniqueid1', ''))
    b2 = channels.get(message.get('Uniqueid2', ''))

    if not b1 and not b2:
        return

    if b1 and b2:
        await b1.bridged.add(b2)
        await b2.bridged.add(b1)

    call: Call = b1.call or b2.call

    if not call:
        return

    if message.get('Bridgestate', '') == 'Link':
        call.state = CallState.CONNECTED
        call.voice_started_at = datetime.now()

    if call.call_type == CallType.INCOMING:
        call.request_pin = b1.pin or b2.pin or call.request_pin

        for num in (
                validate_numbers(b1.from_number, b1.request_number),
                validate_numbers(b2.from_number, b2.request_number),
                validate_numbers(message.get('CallerID1', ''), message.get('CallerID2', ''))
        ):
            if not is_group_numbers(call.request_pin):
                break
            elif num and num.request_pin:
                call.request_pin = num.request_pin
            elif num and num.from_pin:
                call.request_pin = num.from_pin

    await call.save()


async def join(manager: Manager, message: Message):
    queue = message.get('Queue', '')
    call = calls.get(message.get('Uniqueid', ''))

    if queue not in app_config.ats.group_numbers:
        app_config.ats.group_numbers.append(queue)

    if call:
        call.request_pin = queue
        if call.call_type == CallType.UNKNOWN:
            call.call_type = CallType.INCOMING
        await call.save()


async def dial(manager: Manager, message: Message):
    if message.get('SubEvent', '') != 'Begin':
        return

    pin = get_internal(message.get('Dialstring', ''))
    if not pin:
        return

    id1, id2 = message.get('UniqueID', ''), message.get('DestUniqueID', '')
    for ch in (channels.get(id1), channels.get(id2)):
        if ch and not ch.pin:
            ch.pin = pin
            await ch.save()


def register(manager: Manager):
    manager.register_event('Bridge', bridge)
    manager.register_event('Hangup', hangup)
    manager.register_event('Join', join)
    manager.register_event('Newchannel', new_channel)
    manager.register_event('Newstate', new_state)
    manager.register_event('VarSet', var_set)
    manager.register_event('Dial', dial)
    # manager.register_event('Leave', not_used)
    # manager.register_event('Masquerade', not_used)
