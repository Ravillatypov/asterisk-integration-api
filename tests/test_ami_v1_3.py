from unittest.mock import patch

from app.asterisk.cache import calls
from app.consts import CallType, CallState
from app.models import Channel, Call
from tests.fixtures.v1_3 import events1
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

    with patch('app.asterisk.utils.GROUP_NUMBERS', ('9998',)):
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
