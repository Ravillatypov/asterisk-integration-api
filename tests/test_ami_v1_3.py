from app.asterisk.cache import calls
from app.consts import CallType, CallState
from app.models import Channel, Call
from tests.fixtures.v1_3 import events1, events2, events3, events4, events5, events6
from tests.utils import handle_message


async def test_create_call(manager_v1_3):
    assert await Channel.all().count() == 0

    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/2040404-00000727",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "79172471652",
        "CallerIDName": "",
        "AccountCode": "",
        "Exten": "78432041738",
        "Context": "from-trunk",
        "Uniqueid": "1588327327.4649",
    })
    ch = await Channel.filter(id='1588327327.4649').prefetch_related('call').first()
    call = await Call.filter(id='1588327327.4649').first()

    assert ch is not None
    assert call is not None

    assert ch.call.id == call.id
    assert call.from_number == '79172471652'
    assert call.request_number == '78432041738'
    assert call.call_type == CallType.UNKNOWN


async def test_create_channel(manager_v1_3):
    assert await Channel.all().count() == 0

    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "Local/302@from-queue-00000581;1",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "",
        "CallerIDName": "",
        "AccountCode": "",
        "Exten": "302",
        "Context": "from-queue",
        "Uniqueid": "1588327351.4650",
    })

    assert await Channel.filter(id='1588327351.4650').exists() == True
    assert await Call.filter(id='1588327351.4650').exists() == False


async def test_call_incoming_end(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/2040404-00000727",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "79172471652",
        "CallerIDName": "",
        "AccountCode": "",
        "Exten": "78432041738",
        "Context": "from-trunk",
        "Uniqueid": "1588327327.4649",
    })
    call = calls.get('1588327327.4649')

    assert call is not None
    assert call.state == CallState.NEW

    await handle_message(manager_v1_3, {
        "Event": "Newstate",
        "Channel": "SIP/2040404-00000727",
        "ChannelState": "4",
        "ChannelStateDesc": "Ring",
        "CallerIDNum": "79172471652",
        "CallerIDName": "",
        "ConnectedLineNum": "",
        "ConnectedLineName": "",
        "Uniqueid": "1588327327.4649"
    })

    assert call.state == CallState.NEW
    assert call.from_number == '79172471652'
    assert call.request_number == '78432041738'

    await handle_message(manager_v1_3, {
        "Event": "Newstate",
        "Channel": "SIP/2040404-00000727",
        "ChannelState": "6",
        "ChannelStateDesc": "Up",
        "CallerIDNum": "79172471652",
        "CallerIDName": "79172471652",
        "ConnectedLineNum": "",
        "ConnectedLineName": "",
        "Uniqueid": "1588327327.4649"
    })

    assert call.state == CallState.NEW
    assert call.from_number == '79172471652'
    assert call.request_number == '78432041738'

    await handle_message(manager_v1_3, {
        "Event": "Join",
        "Channel": "SIP/2040404-00000727",
        "CallerIDNum": "79172471652",
        "CallerIDName": "79172471652",
        "ConnectedLineNum": "unknown",
        "ConnectedLineName": "unknown",
        "Queue": "9998",
        "Position": "1",
        "Count": "1",
        "Uniqueid": "1588327327.4649",
    })

    assert call.state == CallState.NEW
    assert call.from_number == '79172471652'
    assert call.request_number == '78432041738'
    assert call.request_pin == '9998'
    assert call.call_type == CallType.INCOMING

    for e in events1:
        await handle_message(manager_v1_3, e)

    assert call.state == CallState.NEW
    assert call.from_number == '79172471652'
    assert call.request_number == '78432041738'
    assert call.request_pin == '9998'
    assert call.call_type == CallType.INCOMING
    assert await Call.all().count() == 1
    assert call.voice_started_at is None

    await handle_message(manager_v1_3, {
        "Event": "Bridge",
        "Bridgestate": "Link",
        "Bridgetype": "core",
        "Channel1": "SIP/2040404-00000727",
        "Channel2": "Local/302@from-queue-00000581;1",
        "Uniqueid1": "1588327327.4649",
        "Uniqueid2": "1588327351.4650",
        "CallerID1": "79172471652",
        "CallerID2": "302"
    })
    assert call.state == CallState.CONNECTED
    assert call.request_pin == '302'
    assert call.voice_started_at is not None

    for e in events2:
        await handle_message(manager_v1_3, e)

    assert call.state == CallState.CONNECTED

    await handle_message(manager_v1_3, {
        "Event": "Hangup",
        "Channel": "SIP/2040404-00000727",
        "Uniqueid": "1588327327.4649",
        "CallerIDNum": "79172471652",
        "CallerIDName": "79172471652",
        "ConnectedLineNum": "<unknown>",
        "ConnectedLineName": "<unknown>",
        "AccountCode": "",
        "Cause": "16",
        "Cause-txt": "Normal Clearing"
    })
    assert call.state == CallState.END
    assert call.finished_at is not None
    assert await call.records.all().count() == 1


async def test_call_incoming_missed(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/2040404-00000737",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "79033432950",
        "CallerIDName": "",
        "AccountCode": "",
        "Exten": "78432041738",
        "Context": "from-trunk",
        "Uniqueid": "1588328212.4689"
    })
    call = calls.get('1588328212.4689')
    assert call is not None

    for e in events4:
        await handle_message(manager_v1_3, e)

    assert call.state == CallState.MISSED
    assert call.voice_started_at is None


async def test_call_internal_not_connected(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/303-00001037",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "303",
        "CallerIDName": "Олег",
        "AccountCode": "",
        "Exten": "314",
        "Context": "from-internal",
        "Uniqueid": "1588664567.10633"
    })
    call = calls.get('1588664567.10633')
    assert call is not None
    assert call.state == CallState.NEW
    assert call.from_pin == '303'
    assert call.request_pin == '314'
    assert call.call_type == CallType.INTERNAL

    for e in events5:
        await handle_message(manager_v1_3, e)

    assert call.state == CallState.NOT_CONNECTED
    assert call.voice_started_at is None


async def test_call_internal_end(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/303-00001039",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "303",
        "CallerIDName": "Олег",
        "AccountCode": "",
        "Exten": "314",
        "Context": "from-internal",
        "Uniqueid": "1588664582.10635"
    })
    call = calls.get('1588664582.10635')
    assert call is not None
    assert call.call_type == CallType.INTERNAL

    for e in events6:
        await handle_message(manager_v1_3, e)

    assert call.voice_started_at is not None
    assert call.state == CallState.END


async def test_call_outbound_end(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/314-00000733",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "314",
        "CallerIDName": "314",
        "AccountCode": "",
        "Exten": "89172812810",
        "Context": "from-internal",
        "Uniqueid": "1588328118.4685"
    })
    call = calls.get('1588328118.4685')
    assert call is not None
    assert call.state == CallState.NEW
    assert call.call_type == CallType.OUTBOUND
    assert call.from_pin == '314'
    assert call.request_number == '89172812810'

    for e in events3:
        await handle_message(manager_v1_3, e)

    assert call.state == CallState.NEW
    assert call.from_pin == '314'
    assert call.request_number == '89172812810'

    await handle_message(manager_v1_3, {
        "Event": "Bridge",
        "Bridgestate": "Link",
        "Bridgetype": "core",
        "Channel1": "SIP/314-00000733",
        "Channel2": "SIP/2041738-00000734",
        "Uniqueid1": "1588328118.4685",
        "Uniqueid2": "1588328118.4686",
        "CallerID1": "314",
        "CallerID2": "89172812810"
    })

    assert call.state == CallState.CONNECTED
    assert call.voice_started_at is not None

    await handle_message(manager_v1_3, {
        "Event": "Hangup",
        "Channel": "SIP/314-00000733",
        "Uniqueid": "1588328118.4685",
        "CallerIDNum": "314",
        "CallerIDName": "пункт выдачи не раб",
        "ConnectedLineNum": "89172812810",
        "ConnectedLineName": "CID:314",
        "AccountCode": "",
        "Cause": "16",
        "Cause-txt": "Normal Clearing"
    })
    assert call.state == CallState.END
    assert call.finished_at is not None


async def test_call_outbound_not_connected(manager_v1_3):
    await handle_message(manager_v1_3, {
        "Event": "Newchannel",
        "Channel": "SIP/209-00000797",
        "ChannelState": "0",
        "ChannelStateDesc": "Down",
        "CallerIDNum": "209",
        "CallerIDName": "209",
        "AccountCode": "",
        "Exten": "2628818",
        "Context": "from-internal",
        "Uniqueid": "1588333043.4915"
    })
    call = calls.get('1588333043.4915')
    assert call is not None
    assert call.call_type == CallType.OUTBOUND
    assert call.state == CallState.NEW
