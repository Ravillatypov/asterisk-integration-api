from aiomisc.service.periodic import PeriodicService

from ..consts import IntegrationState, CallState
from ..models import CallRecord
from ..utils import upload_record


class UploadService(PeriodicService):
    interval = 5  # seconds
    delay = 10
    __required__ = ()

    async def callback(self):
        async for record in CallRecord.filter(
                call__state=CallState.END,
                converted__isnull=False,
        ).prefetch_related('call'):
            if await upload_record({'x-call-id': record.call.id, 'x-duration': f'{record.duration}'}, record.converted):
                record.call.integration_state = IntegrationState.UPLOADED
                await record.call.save()
