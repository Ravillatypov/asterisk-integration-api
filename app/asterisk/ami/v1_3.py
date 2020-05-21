from panoramisk.manager import Manager
from panoramisk.message import Message

from app.asterisk.cache import calls, channels
from app.asterisk.utils import validate_numbers, get_call_type, is_group_numbers
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
        ch2 = await ch.bridged.filter(call__not_isnull=True).first()
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
    if call.state == CallState.CONNECTED:
        call.state = CallState.END
    elif call.call_type == CallType.INCOMING:
        call.state = CallState.MISSED
    else:
        call.state = CallState.NOT_CONNECTED
    calls.pop(call.id)


async def bridge(manager: Manager, message: Message):
    if message.get('Bridgestate', '') != 'Link':
        return

    b1 = channels.get(message.get('Uniqueid1', ''))
    b2 = channels.get(message.get('Uniqueid2', ''))

    if not b1 and not b2:
        return

    call: Call = b1.call or b2.call
    await b1.bridged.add(b2)
    await b2.bridged.add(b1)

    num = validate_numbers(message.get('CallerID1', ''), message.get('CallerID12', ''))
    if call and num and call.call_type == CallType.INCOMING:
        call.request_pin = num.request_pin or call.request_pin
        await call.save()


async def join(manager: Manager, message: Message):
    call = calls.get(message.get('Uniqueid', ''))
    if call:
        call.request_pin = message.get('Queue', '')
        await call.save()


def register(manager: Manager):
    manager.register_event('Bridge', bridge)
    manager.register_event('Hangup', hangup)
    manager.register_event('Join', join)
    manager.register_event('Newchannel', new_channel)
    manager.register_event('Newstate', new_state)
    manager.register_event('VarSet', var_set)

    # manager.register_event('Dial', not_used)
    # manager.register_event('Leave', not_used)
    # manager.register_event('Masquerade', not_used)
