from aiomisc.service.periodic import PeriodicService

from app.consts import CallState, IntegrationState
from app.models import CallRecord
from app.utils import get_mp3_file_duration, convert_record, get_full_path


class ConvertService(PeriodicService):
    interval = 10  # seconds
    delay = 5
    __required__ = ()

    async def callback(self):
        async for record in CallRecord.filter(
                converted=None,
                call__state=CallState.END,
                call__integration_state__not=IntegrationState.UPLOADED,
                call__record=None,
        ).prefetch_related('call'):
            path = get_full_path(record.file_name)

            record.converted = convert_record(path, record.call_id)
            record.duration = await get_mp3_file_duration(record.converted)

            if record.converted:
                await record.save()
                record.call.record = record
                await record.call.save()
