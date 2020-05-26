from aiomisc.service.periodic import PeriodicService

from ..consts import CallState, IntegrationState
from ..models import CallRecord
from ..utils import get_mp3_file_duration, convert_record, get_full_path


class ConvertService(PeriodicService):
    interval = 10  # seconds
    delay = 5
    __required__ = ()

    async def callback(self):
        async for record in CallRecord.filter(
                converted__isnull=True,
                call__state=CallState.END,
                call__integration_state__not=IntegrationState.UPLOADED
        ):
            path = get_full_path(record.file_name)

            record.converted = convert_record(path, record.call_id)
            record.duration = await get_mp3_file_duration(record.converted)

            if record.converted:
                await record.save()
