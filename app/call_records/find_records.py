from aiomisc.service.periodic import PeriodicService

from ..asterisk.utils import find_call_record
from ..consts import CallState, IntegrationState
from ..models import Call


class FindRecordService(PeriodicService):
    interval = 10  # seconds
    delay = 10
    __required__ = ()

    async def callback(self):
        async for call in Call.filter(
                state=CallState.END,
                record=None,
                integration_state=IntegrationState.END
        ):
            record = await find_call_record(call)
            if record:
                record.call = call
                await record.save()
            else:
                call.integration_state = IntegrationState.NOT_FOUNDED
                await call.save()
