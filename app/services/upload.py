from aiomisc.service.periodic import PeriodicService

from app.consts import IntegrationState, CallState
from app.models import CallRecord
from app.utils import upload_record


class UploadService(PeriodicService):
    interval = 5  # seconds
    delay = 10
    __required__ = ()

    async def callback(self):
        async for record in CallRecord.filter(
                call__state=CallState.END,
        ).exclude(converted=None).prefetch_related('call'):
            if await upload_record({'x-call-id': record.call.id, 'x-duration': f'{record.duration}'}, record.converted):
                record.call.integration_state = IntegrationState.UPLOADED
                await record.call.save()
